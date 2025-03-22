'''
Routines to compute *partial* Radial distribution functions
of atoms
'''

from ase import Atoms
import numpy as np


def get_instant_rdf(atoms, A='*', B='*', Rmax=5.2, dR=0.02, mic=True):
    '''
    Compute radial distribution functions of atoms,
    as a number of neighbors,
    including partial functions, A-A, A-B, B-A, B-B.

    (Memory-demanding algorithm)

    No volume information required in used notation, so that
    the coordination number can be obtained as a direct summation
    within the limits of coordination shell radii, i.e.:

    `N1 = \sum_{R_i<R1min}^{R1max} rdf(R_i)`

    Parameters:

    atoms: ase.Atoms
        system to analyze
    A, B: str
        atom types. '*' - any atom
    Rmax, dR: float
        maximal distance and step
    mic: bool
        minimal image convention - True to inlcude atoms from
        neighboring periocid cells

    Returns:

    distance grid, total counds, 4 partial counts

    '''
    R = np.arange(0, Rmax+dR/2, dR)
    N = len(atoms)

    dist_list_all  = []
    dist_list_AA = []
    dist_list_AB = []
    dist_list_BA = []
    dist_list_BB = []

    dist_matrix = atoms.get_all_distances(mic=mic)

    chems = atoms.get_chemical_symbols()

    for i1, C1 in enumerate(chems):
        for i2, C2 in enumerate(chems):
            if i2 != i1:
                dist = dist_matrix[i1, i2]
                if dist <= Rmax:
                    dist_list_all.append(dist)
                    if (A == '*') or (C1 == A):
                        if (A == '*') or (C2 == A):
                            dist_list_AA.append(dist)
                        elif (B == '*')or(C2 == B):
                            dist_list_AB.append(dist)
                    elif (B == '*')or(C1 == B):
                        if (A == '*')or(C2 == A):
                            dist_list_BA.append(dist)
                        elif (B == '*')or(C2 == B):
                            dist_list_BB.append(dist)
    if A == '*':
        nA = N
    else:
        nA = chems.count(A)
    if B == '*':
        nB = N
    else:
        nB = chems.count(B)

    digs = np.digitize(x=np.array(dist_list_all), bins=R, right=True)
    counts_all = np.bincount(digs, minlength=len(R)) / N

    if nA > 0:
        digs = np.digitize(x=np.array(dist_list_AA), bins=R, right=True)
        counts_AA = np.bincount(digs, minlength=len(R)) / nA
        digs = np.digitize(x=np.array(dist_list_AB), bins=R, right=True)
        counts_AB = np.bincount(digs, minlength=len(R)) / nA
    else:
        counts_AA = np.zeros(len(R))
        counts_AB = np.zeros(len(R))

    if nB > 0:
        digs = np.digitize(x=np.array(dist_list_BA), bins=R, right=True)
        counts_BA = np.bincount(digs, minlength=len(R)) / nB
        digs = np.digitize(x=np.array(dist_list_BB), bins=R, right=True)
        counts_BB = np.bincount(digs, minlength=len(R)) / nB
    else:
        counts_BA = np.zeros(len(R))
        counts_BB = np.zeros(len(R))

    return R, counts_all, counts_AA, counts_AB, counts_BA, counts_BB


def get_mean_rdf(images, A='*', B='*', Rmax=5.2, dR=0.02, mic=True,
                 imageIdx=None):
    '''
    Get partial RDF averaged over atomic configurations (images)

    Parameters:

    A, B, Rmax, dR, mic:
        same meaning as for get_instant_rdf_mem
    imageIdx: int/slice/None
            Images to analyze

    Result:
        distance grid, total counds, partial counts: A-A, A-B, B-A, B-B
    '''
    if imageIdx is None:
        traj = images
    else:
        traj = images[imageIdx]
    medium_rdf = 0
    medium_rdf_BB = 0
    medium_rdf_BA = 0
    medium_rdf_AB = 0
    medium_rdf_AA = 0
    R = None
    counts = len(traj)
    for atoms in traj:
        R, rdf_all, rdf_AA, rdf_AB, rdf_BA, rdf_BB = \
            get_instant_rdf(atoms, A, B, Rmax, dR, mic)
        medium_rdf += rdf_all / counts
        medium_rdf_BB += rdf_BB / counts
        medium_rdf_BA += rdf_BA / counts
        medium_rdf_AB += rdf_AB / counts
        medium_rdf_AA += rdf_AA / counts

    return R, medium_rdf, medium_rdf_AA, medium_rdf_AB, \
           medium_rdf_BA, medium_rdf_BB
