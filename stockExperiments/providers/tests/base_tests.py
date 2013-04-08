import unittest
from mockito import mock, when, verify, inorder, any as anyv
import util.classutils as classutils
import providers.base as base


class TestAbstractProvider(unittest.TestCase):

    def test_should_have_load_method_with_symbol_argument(self):
        p = base.AbstractProvider()
        self.assertRaises(NotImplementedError, p.load, "")

    def test_should_have_typifies_method_without_arguments(self):
        p = base.AbstractProvider()
        self.assertRaises(NotImplementedError, p.typifies)


class TestAbstractCachingProvider(unittest.TestCase):

    def test_should_have_update_method_with_symbol_and_data_arguments(self):
        p = base.AbstractCachingProvider()
        self.assertRaises(NotImplementedError, p.update, "", object())


class TestRawProvider(unittest.TestCase):

    def test_typifies_should_return_class(self):
        p = base.RawProvider()
        assert p.typifies() is p.__class__
        assert p.typifies() is base.RawProvider

    def test_subclasses_typifies_should_return_class(self):
        l_instances = classutils.instantiate(classutils.get_all_subclasses(base.RawProvider))
        for instance in l_instances:
            assert instance.typifies() is instance.__class__
            assert isinstance(instance, base.RawProvider)


class TestByproductProvider(unittest.TestCase):

    def test_typifies_should_return_class(self):
        p = base.ByproductProvider(mock())
        assert p.typifies() is p.__class__
        assert p.typifies() is base.ByproductProvider

    def test_subclasses_typifies_should_return_class(self):
        l_instances = classutils.instantiate(classutils.get_all_subclasses(base.ByproductProvider), mock())
        for instance in l_instances:
            assert instance.typifies() is instance.__class__
            assert isinstance(instance, base.ByproductProvider)

    def test_init_should_expect_locator_setting_it_as_an_attribute(self):
        locatorMock = mock()
        p = base.ByproductProvider(locatorMock)
        assert p.locator is locatorMock


class TestProviderChainManager(unittest.TestCase):

    def test_should_subclass_abstractProvider(self):
        provider = base.ProviderChainManager()
        assert isinstance(provider, base.AbstractProvider)

    def test_load_should_return_None_if_no_providers_where_registered(self):
        provider = base.ProviderChainManager()
        assert provider.load("") is None

    def test_load_should_delegate_to_registered_providers(self):
        s_symbol = ""

        providerMock1 = mock(base.AbstractProvider)
        providerMock2 = mock(base.AbstractProvider)
        providerMock3 = mock(base.AbstractProvider)
        when(providerMock1).load(s_symbol).thenReturn(None)
        when(providerMock2).load(s_symbol).thenReturn(None)
        when(providerMock3).load(s_symbol).thenReturn(None)

        provider = base.ProviderChainManager(providerMock1, providerMock2, providerMock3)
        provider.load(s_symbol)

        inorder.verify(providerMock1, times=1).load(s_symbol)
        inorder.verify(providerMock2, times=1).load(s_symbol)
        inorder.verify(providerMock3, times=1).load(s_symbol)

    def test_load_should_delegate_sequentially_till_one_returns_data(self):
        s_symbol = ""
        l_data = ["Sample data"]

        providerMock1 = mock(base.AbstractProvider)
        providerMock2 = mock(base.AbstractProvider)
        providerMock3 = mock(base.AbstractProvider)
        when(providerMock1).load(s_symbol).thenReturn(None)
        when(providerMock2).load(s_symbol).thenReturn(l_data)
        when(providerMock3).load(s_symbol).thenReturn(None)

        provider = base.ProviderChainManager(providerMock1, providerMock2, providerMock3)
        result = provider.load(s_symbol)

        assert result == l_data
        inorder.verify(providerMock1, times=1).load(s_symbol)
        inorder.verify(providerMock2, times=1).load(s_symbol)
        inorder.verify(providerMock3, times=0).load(s_symbol)

    def test_load_should_update_providers_that_had_no_data(self):
        s_symbol = ""
        l_data = ["Sample data"]

        providerMock1 = mock(base.AbstractProvider)
        providerMock2 = mock(base.AbstractProvider)
        providerMock3 = mock(base.AbstractProvider)
        when(providerMock1).load(s_symbol).thenReturn(None)
        when(providerMock2).load(s_symbol).thenReturn(None)
        when(providerMock3).load(s_symbol).thenReturn(l_data)

        provider = base.ProviderChainManager(providerMock1, providerMock2, providerMock3)
        result = provider.load(s_symbol)

        assert result == l_data
        inorder.verify(providerMock1, times=1).load(s_symbol)
        inorder.verify(providerMock2, times=1).load(s_symbol)
        inorder.verify(providerMock3, times=1).load(s_symbol)

        inorder.verify(providerMock3, times=0).update(anyv(), anyv())
        inorder.verify(providerMock2, times=1).update(s_symbol, l_data)
        inorder.verify(providerMock1, times=1).update(s_symbol, l_data)

    def test_typifies_should_delegate_to_base_provider(self):
        providerMock1 = mock(base.AbstractProvider)
        providerMock2 = mock(base.AbstractProvider)
        providerMock3 = mock(base.AbstractProvider)
        when(providerMock3).typifies().thenReturn(providerMock3.__class__)
        provider = base.ProviderChainManager(providerMock1, providerMock2, providerMock3)
        assert provider.typifies() is providerMock3.__class__


class TestCachedProvider(unittest.TestCase):

    def test_should_subclass_abstractProvider(self):
        provider = base.CachedProvider(mock())
        assert isinstance(provider, base.AbstractProvider)

    def test_load_should_return_None_if_symbol_data_not_present(self):
        dataMapMock = mock(base.SymbolMap)
        dataMock = []
        s_symbol = ""

        when(dataMapMock).get(s_symbol).thenReturn(dataMock)

        provider = base.CachedProvider(dataMapMock)
        result = provider.load(s_symbol)

        assert result is None
        verify(dataMapMock, times=1).get(anyv())

    def test_load_should_return_data_if_symbol_data_is_present(self):
        dataMapMock = mock(base.SymbolMap)
        dataMock = ["Sample Data"]
        s_symbol = ""

        when(dataMapMock).get(s_symbol).thenReturn(dataMock)

        provider = base.CachedProvider(dataMapMock)
        result = provider.load(s_symbol)

        assert result is dataMock
        verify(dataMapMock, times=1).get(anyv())

    def test_update_should_update_dataMap(self):
        dataMapMock = mock(base.SymbolMap)
        dataMock = mock()
        newData = mock()
        s_symbol = ""

        when(dataMapMock).get(s_symbol).thenReturn(dataMock)

        provider = base.CachedProvider(dataMapMock)
        provider.update(s_symbol, newData)

        verify(dataMock, times=1).update(newData)


class TestCachedProviderWithSymbolMap(unittest.TestCase):

    def test_load_when_nothing_was_updated_should_return_None(self):
        s_symbol = "SYMB11"
        provider = base.CachedProvider(base.SymbolMap())
        assert provider.load(s_symbol) is None

    def test_load_after_data_was_updated_should_return_data(self):
        s_symbol = "SYMB11"
        data = {
                "a": 0,
                "b": 1,
                "c": 2
                }
        provider = base.CachedProvider(base.SymbolMap())
        provider.update(s_symbol, data)
        result = provider.load(s_symbol)
        assert len(result) == 3


class TestSymbolMapFactory(unittest.TestCase):

    def test_get_should_return_instance_of_symbolMap(self):
        factory = base.SymbolMapFactory()
        assert isinstance(factory.get(), base.SymbolMap)

    def test_get_should_return_different_instance_each_call(self):
        factory = base.SymbolMapFactory()
        obj1 = factory.get()
        obj2 = factory.get()

        assert type(obj1) is type(obj2)
        assert obj1 is not obj2


class TestSymbolMap(unittest.TestCase):

    def test_get_should_return_an_dict_instance(self):
        symbolMap = base.SymbolMap()
        s_symbol = "A"
        data = symbolMap.get(s_symbol)
        assert isinstance(data, dict)

    def test_get_should_return_empty_dict_for_not_present_symbols(self):
        symbolMap = base.SymbolMap()
        s_symbol = "A"
        data = symbolMap.get(s_symbol)
        assert len(data) == 0

    def test_get_should_return_different_instances_for_different_symbols(self):
        symbolMap = base.SymbolMap()
        s_symbol1 = "A"
        s_symbol2 = "B"
        data1 = symbolMap.get(s_symbol1)
        data2 = symbolMap.get(s_symbol2)
        assert data1 is not data2

    def test_get_should_return_same_instance_for_same_symbol(self):
        symbolMap = base.SymbolMap()
        s_symbol = "A"
        data1 = symbolMap.get(s_symbol)
        data2 = symbolMap.get(s_symbol)
        assert data1 is data2
