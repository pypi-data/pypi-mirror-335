import pytest


def test_node_marker(pytester: pytest.Pytester):
    pytester.makepyfile(
        """
        import pytest
        from pytest_funcnodes import nodetest

        @nodetest()
        async def test_node():
            assert True
    """
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1)


def test_all_nodes_tested_simple(pytester: pytest.Pytester):
    pytester.makepyfile(
        """
        import pytest
        from pytest_funcnodes import nodetest, all_nodes_tested
        import funcnodes_core as fn

        @fn.NodeDecorator("testnode")
        def testnode():
            pass

        shelf = fn.Shelf(
        name="Test Shelf",
        nodes=[testnode]

            )

        @nodetest(testnode)
        async def test_node():
            assert True

        def test_all_nodes_tested(all_nodes):
            all_nodes_tested(all_nodes,shelf)

    """
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=2)


def test_all_nodes_tested_simple_fail(pytester: pytest.Pytester):
    pytester.makepyfile(
        """
        import pytest
        from pytest_funcnodes import nodetest, all_nodes_tested
        import funcnodes_core as fn

        @fn.NodeDecorator("testnode")
        def testnode():
            pass

        shelf = fn.Shelf(
        name="Test Shelf",
        nodes=[testnode]

            )

        def test_all_nodes_tested(all_nodes):
            all_nodes_tested(all_nodes,shelf)

    """
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(failed=1)


def test_all_nodes_tested_ignore_node(pytester: pytest.Pytester):
    pytester.makepyfile(
        """
        import pytest
        from pytest_funcnodes import nodetest, all_nodes_tested
        import funcnodes_core as fn

        @fn.NodeDecorator("testnode")
        def testnode():
            pass

        shelf = fn.Shelf(
        name="Test Shelf",
        nodes=[testnode]

            )

        def test_all_nodes_tested(all_nodes):
            all_nodes_tested(all_nodes,shelf,ignore=[testnode])

    """
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1)


def test_all_nodes_tested_ignore_shelf(pytester: pytest.Pytester):
    pytester.makepyfile(
        """
        import pytest
        from pytest_funcnodes import nodetest, all_nodes_tested
        import funcnodes_core as fn

        @fn.NodeDecorator("testnode")
        def testnode():
            pass

        shelf = fn.Shelf(
        name="Test Shelf",
        nodes=[testnode]
            )

        ignoreshelf = fn.Shelf(
        name="ignoretest Shelf",
        nodes=[testnode]
            )

        def test_all_nodes_tested(all_nodes):
            all_nodes_tested(all_nodes,shelf,ignore=[ignoreshelf])

    """
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1)
