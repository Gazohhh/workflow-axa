from __future__ import annotations

import copy
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/codebase-map'
spec = importlib.util.spec_from_file_location('flow_renderer', SKILL/'scripts/render_report.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class FlowchartTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'fixture'
        shutil.copytree(SKILL/'examples', self.root)
        self.input = self.root/'review.json'
        self.data = renderer.load_json(self.input)

    def render(self):
        self.input.write_text(json.dumps(self.data), encoding='utf-8')
        return renderer.render(self.data, self.root, self.input)

    def test_new_render_rejects_legacy_schema_with_migration_guidance(self):
        self.data['schema_version'] = 1
        with self.assertRaisesRegex(ValueError, 'migrate the layout'):
            self.render()

    def test_existing_schema_one_html_manifest_remains_checkable(self):
        report = self.root/'old.html'
        manifest = {'schema_version':1, 'tool_version':'2.1.0', 'sources':[{'id':'S1', 'path':'PLAN.md', 'sha256':renderer.digest(self.root/'PLAN.md')}]}
        report.write_text('<script type="application/json" id="report-manifest">'+json.dumps(manifest)+'</script>', encoding='utf-8')
        self.assertEqual(renderer.check_report(report, self.root), [])

    def test_default_is_proposed_feature_flow_and_first_tab(self):
        content = self.render()
        self.assertLess(content.index('for="view-proposed"'), content.index('for="view-current"'))
        self.assertIn('id="view-proposed"', content)
        self.assertIn('class="node decision', content)
        self.assertIn('class="node start', content)
        self.assertIn('class="node result', content)
        self.assertNotIn('radial-gradient', content)
        self.assertNotIn('height:490px', content)

    def test_build_plan_cannot_replace_feature_as_default(self):
        self.data['default_view'] = 'build'
        with self.assertRaisesRegex(ValueError, 'feature flow'):
            self.render()

    def test_unknown_default_view_is_rejected(self):
        self.data['default_view'] = 'made-up'
        with self.assertRaisesRegex(ValueError, 'default_view'):
            self.render()

    def test_compare_requires_current_proposed_summary(self):
        self.data['comparison'] = []
        with self.assertRaisesRegex(ValueError, 'change summary'):
            self.render()

    def test_change_summary_must_reference_existing_tasks(self):
        self.data['comparison'][0]['tasks'] = ['NONEXISTENT']
        with self.assertRaisesRegex(ValueError, 'comparison.tasks'):
            self.render()

    def test_unlabelled_decision_branch_is_rejected(self):
        self.data['graphs'][1]['edges'][2]['label'] = ''
        with self.assertRaisesRegex(ValueError, 'decision branch'):
            self.render()

    def test_duplicate_decision_labels_are_rejected(self):
        self.data['graphs'][1]['edges'][3]['label'] = 'Yes'
        with self.assertRaisesRegex(ValueError, 'distinctly labelled exits'):
            self.render()

    def test_diagonal_connector_is_rejected(self):
        self.data['graphs'][0]['edges'][0]['points'][1][1] += 4
        with self.assertRaisesRegex(ValueError, 'orthogonal'):
            self.render()

    def test_connector_through_unrelated_node_is_rejected(self):
        edge = self.data['graphs'][0]['edges'][0]
        edge.update(to='N3', points=[[336,200],[920,200]], label='')
        with self.assertRaisesRegex(ValueError, 'crosses a node'):
            self.render()

    def test_crossing_routes_are_rejected(self):
        edge = copy.deepcopy(self.data['graphs'][0]['edges'][0])
        edge.update({'from':'N4','to':'N2','label':'','points':[[192,424],[192,336],[400,336],[400,100],[628,100],[628,152]]})
        self.data['graphs'][0]['edges'].append(edge)
        with self.assertRaisesRegex(ValueError, 'cross or share'):
            self.render()

    def test_label_mask_over_node_is_rejected(self):
        self.data['graphs'][0]['edges'][0]['label_position'] = [500,200]
        with self.assertRaisesRegex(ValueError, 'label overlaps a node'):
            self.render()

    def test_label_on_its_stroke_is_rejected(self):
        self.data['graphs'][0]['edges'][0]['label_position'] = [396,200]
        with self.assertRaisesRegex(ValueError, '6px gap'):
            self.render()

    def test_reused_attachment_port_is_rejected(self):
        self.data['graphs'][0]['edges'].append(copy.deepcopy(self.data['graphs'][0]['edges'][0]))
        with self.assertRaisesRegex(ValueError, 'distinct ports'):
            self.render()

    def test_off_grid_geometry_is_rejected(self):
        self.data['graphs'][1]['nodes'][0]['x'] += 1
        with self.assertRaisesRegex(ValueError, '4px-grid'):
            self.render()

    def test_node_outside_canvas_is_rejected(self):
        self.data['graphs'][1]['nodes'][0]['x'] = 1280
        with self.assertRaisesRegex(ValueError, 'bounds'):
            self.render()

    def test_more_than_two_highlights_is_rejected(self):
        self.data['graphs'][1]['nodes'][0]['highlight'] = True
        with self.assertRaisesRegex(ValueError, 'two focal'):
            self.render()

    def test_oversized_view_requires_splitting(self):
        graph = self.data['graphs'][0]
        for i in range(4):
            node = copy.deepcopy(graph['nodes'][0]); node['id'] = f'extra{i}'
            graph['nodes'].append(node)
        with self.assertRaisesRegex(ValueError, 'Split the diagram'):
            self.render()

    def test_important_unknowns_are_not_buried_in_appendix(self):
        self.data['state'] = 'draft'
        node = self.data['graphs'][0]['nodes'][0]
        node.update(basis='unknown', uncertainty='Call path needs confirmation.', evidence=[])
        content = self.render()
        self.assertLess(content.index('Call path needs confirmation.'), content.index('<section class="review"'))

    def test_native_view_controls_exist_without_submit_actions(self):
        content = self.render()
        self.assertEqual(content.count('name="diagram-view"'), 3)
        self.assertEqual(len(re.findall(r'<input[^>]+name="diagram-zoom"', content)), 4)
        self.assertNotIn('<form', content)
        self.assertNotIn('type="submit"', content)
        self.assertNotIn('fetch(', content)
        self.assertNotIn('http://', content.replace('http://www.w3.org/2000/svg', ''))

    def test_group_view_preserves_items_without_faking_process_steps(self):
        graph = copy.deepcopy(self.data['graphs'][0])
        graph.update(id='structure', purpose='structure', tab='Structure', title='Formatter ownership', description='Contains the inspected formatter functions; not execution order.', width=800, height=400, edges=[])
        graph['nodes'] = [copy.deepcopy(graph['nodes'][0])]
        graph['nodes'][0].update(label='Formatter functions', note='', x=40, y=40, width=400, height=240, shape='group', items=['format_score', '_legacy_score'])
        self.data['graphs'].append(graph)
        content = self.render()
        self.assertIn('class="node group', content)
        self.assertIn('class="node-item"', content)
        self.assertIn('not execution order', content)

    def test_delivery_order_cannot_invent_dependency(self):
        graph = self.data['graphs'][2]
        graph['nodes'][2]['task_id'], graph['nodes'][3]['task_id'] = 'T3', 'T2'
        graph['nodes'][2]['tasks'], graph['nodes'][3]['tasks'] = ['T3'], ['T2']
        with self.assertRaisesRegex(ValueError, 'Delivery edges'):
            self.render()

    def test_delivery_node_cannot_claim_an_unknown_task(self):
        self.data['graphs'][2]['nodes'][1]['task_id'] = 'UNKNOWN'
        with self.assertRaisesRegex(ValueError, 'task_id'):
            self.render()

    def test_delivery_must_keep_explicit_approval_precondition(self):
        self.data['graphs'][2]['nodes'][0]['precondition'] = 'skip-approval'
        with self.assertRaisesRegex(ValueError, 'task_id'):
            self.render()

    def test_every_view_has_a_native_start_link(self):
        content = self.render()
        links = re.findall(r'data-start-id="([^"]+)"', content)
        self.assertEqual(len(links), len(self.data['graphs']))
        for anchor in links:
            self.assertEqual(content.count(f'<g id="{anchor}" '), 1)
            self.assertIn(f'href="#{anchor}"', content)

    def test_compound_node_ids_cannot_collide_across_views(self):
        for graph_id, node_id in [('A-B', 'C'), ('A', 'B-C')]:
            graph = copy.deepcopy(self.data['graphs'][0])
            graph.update(id=graph_id, purpose='structure', tab=graph_id, edges=[])
            graph['nodes'] = [copy.deepcopy(graph['nodes'][0])]
            graph['nodes'][0]['id'] = node_id
            self.data['graphs'].append(graph)
        content = self.render()
        self.assertIn('id="node-3-A-B-C"', content)
        self.assertIn('id="node-1-A-B-C"', content)

    def test_source_and_acceptance_anchors_survive_redesign(self):
        content = self.render()
        for prefix, collection in [('e','evidence'),('t','tasks'),('r','requirements'),('a','acceptance'),('s','sources')]:
            for item in self.data[collection]:
                self.assertEqual(content.count(f'id="{prefix}-{item["id"]}"'), 1)
        self.assertIn('confirm', (ROOT/'skills/workflow/SPECIALISTS.md').read_text().lower())


if __name__ == '__main__':
    unittest.main()
