import pytest

from main1 import Trie

theAcTrie = Trie()

def test_trie():
    words = ["去死"]
    theAcTrie.prepareWork(words)
    theAcTrie.searchorg("qu死",1)
    theAcTrie.searchorg("去*死",1)
    theAcTrie.searchorg("去 死",2)
    theAcTrie.searchorg("去A 死",1)

