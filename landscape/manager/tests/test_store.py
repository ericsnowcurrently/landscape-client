from landscape.tests.helpers import LandscapeTest

from landscape.manager.store import ManagerStore


class ManagerStoreTest(LandscapeTest):

    def setUp(self):
        super(ManagerStoreTest, self).setUp()
        self.filename = self.makeFile()
        self.store = ManagerStore(self.filename)
        self.store.add_graph(1, u"file 1", u"user1", "")
        self.store.set_graph_accumulate(1, 1234, 1.0)

    def test_get_unknown_graph(self):
        graph = self.store.get_graph(1000)
        self.assertIdentical(graph, None)

    def test_get_graph(self):
        graph = self.store.get_graph(1)
        self.assertEquals(graph, (1, u"file 1", u"user1", ""))

    def test_get_graphs(self):
        graphs = self.store.get_graphs()
        self.assertEquals(graphs, [(1, u"file 1", u"user1", "")])

    def test_get_no_graphs(self):
        self.store.remove_graph(1)
        graphs = self.store.get_graphs()
        self.assertEquals(graphs, [])

    def test_add_graph(self):
        self.store.add_graph(2, u"file 2", u"user2", "")
        graph = self.store.get_graph(2)
        self.assertEquals(graph, (2, u"file 2", u"user2", ""))

    def test_add_graph_with_error(self):
        self.store.add_graph(2, u"file 2", u"user2", "User not found")
        graph = self.store.get_graph(2)
        self.assertEquals(graph, (2, u"file 2", u"user2", "User not found"))

    def test_add_update_graph(self):
        self.store.add_graph(1, u"file 2", u"user2", "")
        graph = self.store.get_graph(1)
        self.assertEquals(graph, (1, u"file 2", u"user2", ""))

    def test_remove_graph(self):
        self.store.remove_graph(1)
        graphs = self.store.get_graphs()
        self.assertEquals(graphs, [])

    def test_remove_unknown_graph(self):
        self.store.remove_graph(2)
        graphs = self.store.get_graphs()
        self.assertEquals(graphs, [(1, u"file 1", u"user1", "")])

    def test_get_accumulate_unknown_graph(self):
        accumulate = self.store.get_graph_accumulate(2)
        self.assertIdentical(accumulate, None)

    def test_set_accumulate_graph(self):
        self.store.set_graph_accumulate(2, 1234, 2.0)
        accumulate = self.store.get_graph_accumulate(2)
        self.assertEquals(accumulate, (2, 1234, 2.0))

    def test_update_accumulate_graph(self):
        self.store.set_graph_accumulate(1, 4567, 2.0)
        accumulate = self.store.get_graph_accumulate(1)
        self.assertEquals(accumulate, (1, 4567, 2.0))
