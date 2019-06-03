"""

Mini-projet d'algo des graphes : renforcement d'un réseau
Auteur : Gérald LIN

"""


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implémentation d'un graphe non orienté à l'aide d'un dictionnaire: les clés
sont les sommets, et les valeurs sont les sommets adjacents à un sommet donné.
Les boucles sont autorisées. Les poids ne sont pas autorisés.

On utilise la représentation la plus simple: une arête {u, v} sera présente
deux fois dans le dictionnaire: v est dans l'ensemble des voisins de u, et u
est dans l'ensemble des voisins de v.
"""


class Graphe(object):
    def __init__(self):
        """Initialise un graphe sans arêtes"""
        self.dictionnaire = dict()
        self.noms = dict()

    def ajouter_arete(self, u, v, ligne):
        """Ajoute une arête entre les sommmets u et v, en créant les sommets
        manquants le cas échéant."""
        # vérification de l'existence de u et v, et création(s) sinon
        if u not in self.dictionnaire:
            self.dictionnaire[u] = set()
            self.noms[u] = None
        if v not in self.dictionnaire:
            self.dictionnaire[v] = set()
            self.noms[v] = None
        # ajout de u (resp. v) parmi les voisins de v (resp. u)
        self.dictionnaire[u].add((v, ligne))
        self.dictionnaire[v].add((u, ligne))

    def ajouter_aretes(self, iterable):
        """Ajoute toutes les arêtes de l'itérable donné au graphe. N'importe
        quel type d'itérable est acceptable, mais il faut qu'il ne contienne
        que des couples d'éléments (quel que soit le type du couple)."""
        for u, v, ligne in iterable:
            self.ajouter_arete(u, v, ligne)

    def ajouter_sommet(self, sommet):
        """Ajoute un sommet (de n'importe quel type hashable) au graphe."""
        u, nom = sommet
        if u not in self.dictionnaire:
            self.dictionnaire[u] = set()
            self.noms[u] = nom

    def ajouter_sommets(self, iterable):
        """Ajoute tous les sommets de l'itérable donné au graphe. N'importe
        quel type d'itérable est acceptable, mais il faut qu'il ne contienne
        que des éléments hashables."""
        for sommet in iterable:
            self.ajouter_sommet(sommet)

    def aretes(self):
        """Renvoie l'ensemble des arêtes du graphe. Une arête est représentée
        par un tuple (a, b) avec a <= b afin de permettre le renvoi de boucles.
        """
        res = set()
        for u in self.dictionnaire:
            for v, ligne in self.dictionnaire[u]:
                tmp = sorted((u, v))
                tmp.append(ligne)
                res.add(tuple(tmp))

        return res

    def boucles(self):
        """Renvoie les boucles du graphe, c'est-à-dire les arêtes reliant un
        sommet à lui-même."""
        return {(u, u) for u in self.dictionnaire if u in self.dictionnaire[u]}

    def contient_arete(self, u, v, ligne):
        """Renvoie True si l'arête {u, v} existe, False sinon."""
        if self.contient_sommet(u) and self.contient_sommet(v):
            return (u, ligne) in self.dictionnaire[v]  # ou v in self.dictionnaire[u]
        return False

    def contient_sommet(self, u):
        """Renvoie True si le sommet u existe, False sinon."""
        return u in self.dictionnaire

    def degre(self, sommet):
        """Renvoie le nombre de voisins du sommet; s'il n'existe pas, provoque
        une erreur."""
        if not self.contient_sommet(sommet):
            raise ValueError("Le sommet n'existe pas.")
        return len(self.dictionnaire[sommet])

    def nombre_aretes(self):
        """Renvoie le nombre d'arêtes du graphe."""
        # attention à la division par 2 (chaque arête étant comptée deux fois)
        return sum(len(voisins) for voisins in self.dictionnaire.values()) // 2

    def nombre_boucles(self):
        """Renvoie le nombre d'arêtes de la forme {u, u}."""
        return len(self.boucles())

    def nombre_sommets(self):
        """Renvoie le nombre de sommets du graphe."""
        return len(self.dictionnaire)

    def retirer_arete(self, u, v, ligne):
        """Retire l'arête {u, v} si elle existe; provoque une erreur sinon."""
        if not self.contient_sommet(u) or not self.contient_sommet(v):
            raise ValueError("Le sommet est invalide.")
            
        self.dictionnaire[u].remove((v, ligne))  # plante si u ou v n'existe pas
        self.dictionnaire[v].remove((u, ligne))  # plante si u ou v n'existe pas

    def retirer_aretes(self, iterable):
        """Retire toutes les arêtes de l'itérable donné du graphe. N'importe
        quel type d'itérable est acceptable, mais il faut qu'il ne contienne
        que des couples d'éléments (quel que soit le type du couple)."""
        for u, v, ligne in iterable:
            self.retirer_arete(u, v, ligne)

    def retirer_sommet(self, sommet):
        """Efface le sommet du graphe, et retire toutes les arêtes qui lui
        sont incidentes."""
        del self.dictionnaire[sommet[0]]
        # retirer le sommet des ensembles de voisins
        for u in self.dictionnaire:
            self.dictionnaire[u].discard(sommet)

    def retirer_sommets(self, iterable):
        """Efface les sommets de l'itérable donné du graphe, et retire toutes
        les arêtes incidentes à ces sommets."""
        for sommet in iterable:
            self.retirer_sommet(sommet)

    def sommets(self):
        """Renvoie l'ensemble des sommets du graphe."""
        return set(self.dictionnaire.keys())

    def sous_graphe_induit(self, iterable):
        """Renvoie le sous-graphe induit par l'itérable de sommets donné."""
        G = Graphe()
        G.ajouter_sommets(iterable)
        for u, v, ligne in self.aretes():
            if G.contient_sommet(u) and G.contient_sommet(v):
                G.ajouter_arete(u, v, ligne)
        return G

    def voisins(self, sommet):
        """Renvoie l'ensemble des voisins du sommet donné."""
        return self.dictionnaire[sommet]

    def nom_sommet(self, elm):
        return self.noms[elm]