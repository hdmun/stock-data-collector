import unittest

from router import Router


class RouterTests(unittest.IsolatedAsyncioTestCase):
    def test_falied_duplicate_path(self):
        def __route_example1():
            pass

        def __route_example2():
            pass

        # given
        router = Router()
        route1 = router.route('/path')
        route2 = router.route('/path')

        # when
        route1(__route_example1)

        # then
        with self.assertRaises(ValueError):
            route2(__route_example2)

    async def test_falied_not_exists_path(self):
        # given
        router = Router()

        # when, then
        with self.assertRaises(ValueError):
            await router.process('/path', None, None)
