"""

Mini-projet d'algo des graphes : renforcement d'un réseau
Auteur : Gérald LIN

"""

from graphe import *
import random
import argparse
import os


def charger_donnees(graphe, fichier):
    with open(fichier, 'r') as my_file:
        # nom du fichier
        name = fichier.split('.')[0]
        text_split = my_file.read().split('# connexions')

        # liste des stations
        lst_stations = text_split[0].lstrip('#stations\n ').rstrip('\n').split('\n')
        for elm in lst_stations:
            station = elm.split(':')
            graphe.ajouter_sommet((int(station[0]), station[1]))
        
        # liste des connexions
        lst_connexions = text_split[1].strip('\n').split('\n')
        for elm in lst_connexions:
            tmp = elm.split('/')
            graphe.ajouter_arete(int(tmp[0]), int(tmp[1]), name)


def init_dict(sommets, valeur):
    res = dict()
    for key in sommets:
        res[key] = valeur
    return res


def numerotations(graphe):
    debut = init_dict(graphe.sommets(), 0)
    parent = init_dict(graphe.sommets(), None)
    ancetre = init_dict(graphe.sommets(), 0)
    instant = 0

    def numerotation_recursive(sommet):
        nonlocal instant
        instant += 1

        # affectation de la date d'exploration et de l'ancêtre
        debut[sommet] = ancetre[sommet] = instant

        # pour tous les voisins triés de sommet
        for u, __not_used__ in sorted(graphe.voisins(sommet), key=lambda elm: elm[0]):

            # si le voisin est déjà exploré
            if debut[u] != 0:
                # si le parent est différent du voisin
                if parent[sommet] != u:
                    ancetre[sommet] = min(ancetre[sommet], debut[u])

            else:
                parent[u] = sommet
                numerotation_recursive(u)
                ancetre[sommet] = min(ancetre[sommet], ancetre[u])

    for u in sorted(graphe.sommets()):
        if debut[u] == 0:
            numerotation_recursive(u)

    return (debut, parent, ancetre)


# renvoie le nombre de successeurs de sommet
def nb_successeurs(sommet, graphe, parent):
    res = 0
    for v, __not_used__ in graphe.voisins(sommet):
        # si parent[v] == sommet, alors v est successeur de sommet
        if parent[v] == sommet:
            res += 1
    return res


def points_articulation(reseau):
    articulations = set()
    debut, parent, ancetre = numerotations(reseau)

    # les racines sont les sommets qui n'ont pas de parent
    racines = set()

    # traitement des racines des arbres d'exploration
    for key in parent:
        if parent[key] == None:
            racines.add(key)
    
    for u in racines:
        deg = nb_successeurs(u, reseau, parent)
        if deg >= 2:
            articulations.add(u)

    # traitement des autres sommets
    racines.add(None)
    for u in reseau.sommets():
        if (parent[u] not in racines) and (ancetre[u] >= debut[parent[u]]):
            articulations.add(parent[u])

    return articulations


def ponts(reseau):
    ponts = set()
    debut, parent, ancetre = numerotations(reseau)
    
    for u in reseau.sommets():
        if (parent[u] != None) and (ancetre[u] > debut[parent[u]]):
            ponts.add((parent[u], u))
    
    return ponts


def csp_feuille(graphe):
    feuilles = set()
    ens_ext = set()
    ens_ponts = ponts(graphe)
    deja_explore = init_dict(graphe.sommets(), False)

    # ensemble des extrémités
    for u, v in ens_ponts:
        ens_ext.add(u)
        ens_ext.add(v)

    # Trouver une composante sans pont à partir d'un sommet u de départ.
    # (u, v) est le pont associé à u.
    # Indique également si cette composante contient plusieurs extrémités de pont.
    def trouver_compo(sommet, pont_associe):
        nonlocal contains_multi_ponts
        compo.add(sommet)
        deja_explore[sommet] = True

        for u, __not_used__ in graphe.voisins(sommet):
            if u in ens_ext:
                if u not in pont_associe:
                    contains_multi_ponts = True

            elif not deja_explore[u]:
                trouver_compo(u, pont_associe)

    # parcours de toutes les extrémités
    for pont in ens_ponts:
        for sommet in pont:
            for key in graphe.sommets():
                deja_explore[key] = False

            contains_multi_ponts = False
            compo = set()
            trouver_compo(sommet, pont)

            # Si la composante créée contient au plus une extrémité de pont
            # alors elle est considérée comme une feuille.
            if not contains_multi_ponts:
                feuilles.add(tuple(compo))

    # l'ensemble des ponts est renvoyé pour éviter de le recalculer dans "amelioration_ponts()"
    return list(feuilles), ens_ponts


def trouver_sous_graphe(graphe):
    feuilles, ens_ponts = csp_feuille(graphe)
    feuille_deja_explo = init_dict(feuilles, False)

    # tableau contenant tous les sous-graphes de "graphe"
    sous_graphe = dict()
    deja_explore = init_dict(graphe.sommets(), False)

    # Parcours des sous-graphes à partir de sommet, si le sommet "cible" est rencontré
    # alors les sommets en paramètre appartenant respectivement à leur CSP feuille
    # font parties du même sous-graphe.
    def meme_sous_graphe(sommet, cible):
        deja_explore[sommet] = True

        # Sommet "cible" rencontré alors la CSP auquel appartient "cible" est dans le
        # même sous-graphe que celui de "sommet".
        if sommet == cible:
            sous_graphe[i].append(feuilles[j])
            feuille_deja_explo[feuilles[j]] = True
        else:
            for u, __not_used__ in graphe.voisins(sommet):
                if not deja_explore[u]:
                    meme_sous_graphe(u, cible)

    # ajout des CSP feuilles à leur sous-graphe
    for i in range(len(feuilles)):
        if not feuille_deja_explo[feuilles[i]]:
            # création d'un nouveau sous-graphe
            sous_graphe[i] = [feuilles[i]]
            feuille_deja_explo[feuilles[i]] = True

            for j in range(i + 1, len(feuilles)):
                if not feuille_deja_explo[feuilles[j]]:
                    for key in graphe.sommets():
                        deja_explore[key] = False

                    meme_sous_graphe(feuilles[i][0], feuilles[j][0])

    return sous_graphe, ens_ponts


# renvoie un ensemble d'arêtes à ajouter pour supprimer les ponts
def amelioration_ponts(reseau):
    aretes_amelioration = set();
    sous_graphe, ens_ponts = trouver_sous_graphe(reseau)
    
    # Vérifie si un sous-graphe est composé uniquement
    # de deux sommets et d'un pont entre.
    def verifier_mini_graphe():
        if len(sg_tmp) == 2 and (len(sg_tmp[0]), len(sg_tmp[1])) == (1, 1):
            nb_voisins_1 = len(reseau.voisins(sg_tmp[0][0]))
            nb_voisins_2 = len(reseau.voisins(sg_tmp[1][0]))
            if nb_voisins_1 == 1 and nb_voisins_2 == 1:
                return True
        return False

    # ajout des arêtes permettant d'améliorer le réseau
    for num_sg in sous_graphe:
        sg_tmp = sous_graphe[num_sg]

        if verifier_mini_graphe():
            aretes_amelioration.add((sg_tmp[0][0], sg_tmp[1][0]))

        else:
            for i in range(len(sg_tmp) - 1):
                # choix aléatoire des sommets
                u = random.choice(sg_tmp[i])
                v = random.choice(sg_tmp[i + 1])
                # Tant que l'arête potentielle à ajouter est identique à un pont
                # on continue de choisir aléatoirement les sommets.
                while (u, v) in ens_ponts or (v, u) in ens_ponts:
                    u = random.choice(sg_tmp[i])
                    v = random.choice(sg_tmp[i + 1])

                aretes_amelioration.add((u, v))
    
    return aretes_amelioration


# renvoie un ensemble d'arêtes à ajouter pour supprimer les points d'articulation
def amelioration_points_articulation(reseau):
    aretes_amelioration = set();
    debut, parent, ancetre = numerotations(reseau)
    ens_artic = points_articulation(reseau)

    # tableau des articulations à traiter
    artic_deja_traite = init_dict(ens_artic, False)
    for point in ens_artic:
        artic_deja_traite[point] = False

    def artic_toutes_traitees():
        nonlocal point_date_max
        for point in artic_deja_traite:
            if not artic_deja_traite[point]:
                point_date_max = point
                return False
        return True

    def trouver_racine(sommet):
        nonlocal racine
        if parent[sommet] == None:
            racine = sommet

        else:
            # si le sommet est un point d'articulation, on considère qu'il a été traité
            # si le nombre de successeurs est >= 2, alors il faudra le traiter séparément
            if (sommet in ens_artic) and (nb_successeurs(sommet, reseau, parent) < 2):
                artic_deja_traite[sommet] = True
            trouver_racine(parent[sommet])

    def est_successeur(voisin, sommet):
        return parent[voisin] == sommet

    def recup_point_date_max():
        nonlocal point_date_max
        for point in ens_artic:
            if (not artic_deja_traite[point]) and (debut[point] > debut[point_date_max]):
                point_date_max = point

    def articulation_non_racine():
        trouver_racine(point_date_max)
        artic_deja_traite[point_date_max] = True

        for v, __not_used__ in reseau.voisins(point_date_max):
            if est_successeur(v, point_date_max) \
            and (v not in ens_artic) \
            and (ancetre[v] >= debut[point_date_max]):
                aretes_amelioration.add((racine, v))

    def articulation_racine():
        # liste des successeurs à relier
        successeurs = list()
        artic_deja_traite[point_date_max] = True
        
        for v, __not_used__ in reseau.voisins(point_date_max):
            if est_successeur(v, point_date_max):
                successeurs.append(v)
        
        for i in range(len(successeurs) - 1):
            aretes_amelioration.add((successeurs[i], successeurs[i + 1]))

    point_date_max = None
    racine = None
    while not artic_toutes_traitees():
        # sélection du point d'articulation dont la date de début est maximale
        recup_point_date_max()

        # cas où le point d'articulation n'est pas une racine
        if parent[point_date_max] != None:
            articulation_non_racine()

        # cas où le point d'articulation est une racine
        else:
            articulation_racine()
    
    return aretes_amelioration


# Fonctions gérant toutes les options du programme :

def option_metro(reseau, args):
    affichage = list()

    if len(args) > 0:
        lst_metro = args
        for line in lst_metro:
            file = 'METRO_' + line + '.txt'
            charger_donnees(reseau, file)
            affichage.append(line)
        print('Chargement des lignes', affichage, 'de metro ... terminé.')

    else:
        files = os.listdir('.')
        for name in files:
            if 'METRO_' in name:
                charger_donnees(reseau, name)
        print('Chargement de toutes les lignes de metro ... terminé.')

def option_rer(reseau, args):
    affichage = list()

    if len(args) > 0:
        lst_rer = args
        for line in lst_rer:
            file = 'RER_' + line.upper() + '.txt'
            charger_donnees(reseau, file)
            affichage.append(line.upper())
        print('Chargement des lignes', affichage, 'de rer ... terminé.')

    else:
        files = os.listdir('.')
        for name in files:
            if 'RER_' in name:
                charger_donnees(reseau, name)
        print('Chargement de toutes les lignes de rer ... terminé.')

def option_liste_stations(reseau):
    print('\nLe réseau contient les', reseau.nombre_sommets(), 'stations suivantes:')
    affichage = set()
    for ident in reseau.sommets():
        affichage.add((reseau.nom_sommet(ident), ident))
    for st in sorted(affichage):
        print('\t-', st[0], '(' + str(st[1]) + ')')

def option_ponts(reseau):
    affichage = set()
    ens_ponts = ponts(reseau)

    print('\nLe réseau contient les', len(ens_ponts), 'ponts suivants:')
    for u, v in ens_ponts:
        affichage.add((reseau.nom_sommet(u), reseau.nom_sommet(v)))
    for st1, st2 in sorted(affichage):
        print('\t-', st1, '--', st2)

def option_articulations(reseau):
    affichage = set()
    ens_artic = points_articulation(reseau)
    i = 1

    print('\nLe réseau contient les', len(ens_artic), 'points d\'articulation suivants:')
    for u in ens_artic:
        affichage.add(reseau.nom_sommet(u))
    for st in sorted(affichage):
        print('\t' + str(i), ':', st)
        i += 1

def option_ameliorer_articulations(reseau):
    aretes_amelioration = amelioration_points_articulation(reseau)
    print('\nOn peut éliminer tous les points d\'articulation du réseau en rajoutant les', len(aretes_amelioration), 'arêtes suivantes:')
    afficher_ameliorations(reseau, aretes_amelioration)

def option_ameliorer_ponts(reseau):
    aretes_amelioration = amelioration_ponts(reseau)
    print('\nOn peut éliminer tous les ponts du réseau en rajoutant les', len(aretes_amelioration), 'arêtes suivantes:')
    afficher_ameliorations(reseau, aretes_amelioration)

def afficher_ameliorations(reseau, ameliorations):
    affichage = set()
    for u, v in ameliorations:
        affichage.add((reseau.nom_sommet(u), reseau.nom_sommet(v)))
    for st1, st2 in sorted(affichage):
        print('\t-', st1, '--', st2)


def args_options(reseau):
    data_loaded = False

    parser = argparse.ArgumentParser(description='Options détectant et améliorant les fragilités dans un réseau.')
    parser.add_argument('--metro',
                        help='charge les lignes de métro dans le réseau',
                        nargs='*',
                        metavar='METRO',
                        dest='metro')

    parser.add_argument('--rer',
                        help='charge les lignes de RER dans le réseau',
                        nargs='*',
                        metavar='RER',
                        dest='rer')

    parser.add_argument('--liste-stations', '-ls',
                        help='affiche les stations du réseau triées par ordre alphabétique',
                        action='store_true',
                        dest='stations')

    parser.add_argument('--articulations',
                        help='affiche les points d’articulation du réseau qui a été chargé',
                        action='store_true',
                        dest='articulations')

    parser.add_argument('--ponts',
                        help='affiche les ponts du réseau qui a été chargé',
                        action='store_true',
                        dest='ponts')

    parser.add_argument('--ameliorer-articulations', '-aa',
                        help='affiche les arêtes à rajouter pour que les stations ne soient plus des points d’articulation',
                        action='store_true',
                        dest='am_artic')

    parser.add_argument('--ameliorer-ponts', '-ap',
                        help='affiche les arêtes à rajouter pour que les arêtes ne soient plus des ponts',
                        action='store_true',
                        dest='am_ponts')

    args = parser.parse_args()

    if args.metro != None:
        data_loaded = True
        option_metro(reseau, args.metro)

    if args.rer != None:
        data_loaded = True
        option_rer(reseau, args.rer)
    
    if data_loaded:
        print('Le réseau contient', reseau.nombre_sommets(), 'sommets et', reseau.nombre_aretes(), 'arêtes.')

        if args.stations:
            option_liste_stations(reseau)

        if args.ponts:
            option_ponts(reseau)

        if args.articulations:
            option_articulations(reseau)

        if args.am_ponts:
            option_ameliorer_ponts(reseau)

        if args.am_artic:
            option_ameliorer_articulations(reseau)

    else:
        print('Aucun réseau n\'a été chargé.')



def main():
    reseau = Graphe()
    args_options(reseau)


if __name__ == "__main__":
    main()