"""Composite reads and nested measurement evidence, checked by finite enumeration."""

import unittest
from unittest.mock import patch

from kaleion import Collection, Workspace
from examples.studio.adapter import Studio, expression


def n(value):
    return {"integer": str(value)}


def f(name):
    return {"field": name}


def op(symbol, left, right):
    return {"op": symbol, "args": [left, right]}


def key(*names):
    return {"tuple": [f(name) for name in names]}


def read(name, on, source_key, value=None):
    return {"read": {"object": name, "on": on, "key": source_key, "value": f("value") if value is None else value}}


def apply(studio, action, name, **args):
    preview = studio.preview(dict(action=action, name=name, args=args), studio.revision)
    studio.commit(preview["token"], studio.revision)


def radon(size):
    studio = Studio()
    apply(studio, "grid", "image", shape=[str(size)]*2, axes=["u", "v"], value=op("*", f("u"), op("+", f("v"), n(1))))
    apply(studio, "grid", "lines", shape=[str(size+1), str(size)], axes=["m", "t"], value=n(0))
    apply(studio, "product", "pairs", factors={"point":dict(source="image", fields=["u", "v", "value"]),
                                               "line":dict(source="lines", fields=["m", "t"])})
    rule = op("or", op("and", op("<", f("line_m"), n(size)),
                                op("=", op("%", op("-", op("-", f("point_v"), op("*", f("line_m"), f("point_u"))), f("line_t")), n(size)), n(0))),
                    op("and", op("=", f("line_m"), n(size)), op("=", f("point_u"), f("line_t"))))
    apply(studio, "lens", "incidence", source="pairs", rule=rule)
    apply(studio, "measure", "counts", source="incidence", by=["line_m", "line_t"], reducer="sum", weight=f("point_value"))
    weight = read("counts", key("line_m", "line_t"), key("line_m", "line_t"))
    apply(studio, "measure", "back", source="incidence", by=["point_u", "point_v"], reducer="sum", weight=weight)
    apply(studio, "lens", "family", source="counts", rule=op("=", f("line_m"), n(0)))
    apply(studio, "measure", "total", source="family", by=[], reducer="sum", weight=f("value"))
    numerator = op("-", f("value"), read("total", n(0), f("key")))
    apply(studio, "field", "recovered", source="back", field="recovered", value=op("//", numerator, n(size)))
    apply(studio, "field", "remainders", source="back", field="remainder", value=op("%", numerator, n(size)))
    return studio


def on_line(size, u, v, m, t):
    return u == t if m == size else (v - m*u) % size == t


class WeightedStudioTests(unittest.TestCase):
    def test_radon_composite_reads_recover_image_and_follow_weights_to_pixels(self):
        for size in (2, 3, 5):
            with self.subTest(size=size):
                studio = radon(size)
                results = studio.workspace.state.results
                expected = [sum(u*(v+1) for u in range(size) for v in range(size) if on_line(size,u,v,m,t))
                            for m in range(size+1) for t in range(size)]
                self.assertEqual(results["counts"].values.tolist(), expected)
                self.assertEqual(results["recovered"].fields["recovered"].tolist(), [u*(v+1) for u in range(size) for v in range(size)])
                self.assertEqual(set(results["remainders"].fields["remainder"]), {0})
                saved = studio.workspace.to_json()
                with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
                    studio.reopen(saved, studio.revision)
                    # Pixel (0,0) receives the line (m=size,t=0), with weight zero.
                    ref = [results["back"].node, results["back"].ids[0]]
                    receipt = studio.contributors(ref, studio.revision)["measurement"]
                    self.assertEqual(receipt["contributor_count"], str(size+1))
                    self.assertTrue(all(c["item"]["value"] == "1" for c in receipt["contributors"]))
                    zero = receipt["contributors"][-1]
                    self.assertEqual(zero["weight"], "0")
                    self.assertEqual(zero["reads"][0]["key"], [str(size), "0"])
                    count = studio.contributors(zero["reads"][0]["driver"], studio.revision)["measurement"]
                    self.assertEqual(count["contributor_count"], str(size))
                    self.assertEqual([c["weight"] for c in count["contributors"]], ["0"]*size)
                    self.assertEqual([c["item"]["fields"]["point_v"] for c in count["contributors"]], list(map(str,range(size))))
                    candidate = studio.inspect_ref(count["contributors"][0]["item"]["ref"], studio.revision)
                    copied_pixel = next(read for read in candidate["bindings"] if read["site"] == "point_value")
                    pixel = studio.inspect_ref(copied_pixel["driver"], studio.revision)["item"]
                    self.assertEqual(pixel["value"], "0")
                    self.assertEqual(pixel["fields"]["u"], "0")
                    self.assertEqual(pixel["fields"]["v"], "0")
                self.assertEqual(studio.workspace.to_json(), saved)

    def test_composite_modulus_does_not_inherit_prime_reconstruction_identity(self):
        size = 4
        studio = radon(size)
        results = studio.workspace.state.results
        expected_counts = {(m,t):sum(u*(v+1) for u in range(size) for v in range(size) if on_line(size,u,v,m,t))
                           for m in range(size+1) for t in range(size)}
        expected_back = [sum(value for (m,t),value in expected_counts.items() if on_line(size,u,v,m,t))
                         for u in range(size) for v in range(size)]
        self.assertEqual(results["back"].values.tolist(), expected_back)
        original = [u*(v+1) for u in range(size) for v in range(size)]
        self.assertNotEqual(results["recovered"].fields["recovered"].tolist(), original)
        self.assertTrue(any(results["remainders"].fields["remainder"]))
        self.assertEqual(results["back"].values[0], 56)
        self.assertEqual(results["recovered"].fields["recovered"][0], -1)
        self.assertEqual(results["remainders"].fields["remainder"][0], 0)

    def test_composite_keys_preserve_order_exact_values_and_repeated_components(self):
        huge = 2**90+1
        driver = Collection.literal([17, 29, 43], fields={"a":[huge, huge, huge+1], "b":[0,1,0]})
        target = Collection.literal([1,1,1], fields={"u":[huge+1,huge,huge], "v":[0,1,0]})
        studio = Studio();studio.workspace=Workspace({"driver":driver,"target":target}, max_items=2000,max_history=40)
        apply(studio,"field","aligned",source="target",field="read",value=read("driver",key("u","v"),key("a","b")))
        self.assertEqual(studio.workspace.state.results["aligned"].fields["read"].tolist(),[43,29,17])
        saved=studio.workspace.to_json()
        for bad in (key("v","u"), f("u")):
            with self.assertRaises(ValueError):
                apply(studio,"field","bad",source="target",field="read",value=read("driver",bad,key("a","b")))
        self.assertEqual(studio.workspace.to_json(),saved)
        for bad in ({"tuple":[]},{"tuple":[n(0)]},{"tuple":[n(0)]*9},{"tuple":"a,b"},{"tuple":[key("u","v"),n(0)]}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):expression(bad,{})

    def test_weight_read_value_is_distinct_from_computed_weight(self):
        studio = Studio()
        apply(studio,"integers","driver",values=["0","2","5"])
        apply(studio,"integers","items",values=["99","99","99"])
        weight = op("-", op("*", n(2),read("driver",f("index"),f("index"))), n(4))
        apply(studio,"measure","sum",source="items",by=[],reducer="sum",weight=weight)
        result=studio.workspace.state.results["sum"]
        receipt=studio.contributors([result.node,result.ids[0]],studio.revision)["measurement"]
        self.assertEqual([c["weight"] for c in receipt["contributors"]],["-4","0","6"])
        self.assertEqual([c["reads"][0]["value"] for c in receipt["contributors"]],["0","2","5"])
        self.assertEqual(receipt["item"]["value"],"2")


if __name__ == "__main__":
    unittest.main()
