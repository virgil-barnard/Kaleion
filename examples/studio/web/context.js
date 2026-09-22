// Availability depends on selection scope and capabilities, never lesson names.
export function actions({mode, object, point, group}) {
  if (mode === 'view') return ['fit'];
  if (mode === 'points') return object?.status === 'ready' && point ? ['explain'] : [];
  if (mode === 'groups') return object?.status === 'ready'
    ? group ? ['group_options', 'group_lens', 'measure', 'coverage'] : ['group_options', 'coverage'] : [];
  const add = ['integers', 'grid'];
  if (!object) return add;
  if (object.status !== 'ready') return add;
  return object.kind === 'incidence'
    ? ['measure', 'coverage', 'select', ...add]
    : ['field', 'lens', 'measure', 'coverage', 'place', 'product', ...add];
}

export const labels = {
  integers: 'Add integers', grid: 'Add a grid', field: 'Define a field',
  lens: 'Create a relation', measure: 'Measure', place: 'Arrange',
  product: 'Form a product', select: 'Keep matching occurrences',
  explain: 'Explain this occurrence', fit: 'Fit view',
  group_options: 'Choose group keys', group_lens: 'Create a group lens',
  coverage: 'Check coverage', assignment: 'Use unique matches',
};
