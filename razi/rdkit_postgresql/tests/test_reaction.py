import unittest

from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, select, func, bindparam

engine = create_engine('postgresql://localhost/razi-rdkit-postgresql-test')
metadata = MetaData(engine)

pg_settings = Table('pg_settings', metadata,
                    autoload=True, autoload_with=engine)


class ReactionBasicTestCase(unittest.TestCase):

    def test_reaction(self):

        conn = engine.connect()

        # dummy query to ensure that GUC params are initialized
        _ = conn.execute(select([ func.rdkit_version() ]))

        stmt = pg_settings.update()
        stmt = stmt.where(pg_settings.c.name == bindparam('param'))
        stmt = stmt.values(setting=bindparam('value'))

        conn.execute(stmt, [
            {'param': 'rdkit.ignore_reaction_agents', 'value': False},
            {'param': 'rdkit.agent_FP_bit_ratio', 'value': 0.2},
            {'param': 'rdkit.difference_FP_weight_agents', 'value': 1},
            {'param': 'rdkit.difference_FP_weight_nonagents', 'value': 10},
            {'param': 'rdkit.move_unmmapped_reactants_to_agents',
             'value': True},
            {'param': 'rdkit.threshold_unmapped_reactant_atoms',
             'value': 0.2},
            {'param': 'rdkit.init_reaction', 'value': True},
            ])

        rs = conn.execute(
            select([func.reaction_from_smiles('c1ccccc1>>c1cccnc1')])
            )
        self.assertEqual(rs.fetchall()[0][0], 'c1ccccc1>>c1ccncc1')

        rs = conn.execute(
            select([func.reaction_from_smiles('c1ccccc1>CC(=O)O>c1cccnc1')])
            )
        self.assertEqual(rs.fetchall()[0][0], 'c1ccccc1>CC(=O)O>c1ccncc1')

        rs = conn.execute(
            select([func.reaction_from_smarts('[c1:1][c:2][c:3][c:4]c[c1:5]>CC(=O)O>[c1:1][c:2][c:3][c:4]n[c1:5]')])
            )
        self.assertEqual(rs.fetchall()[0][0], 'c([cH:4][cH:3][cH:2][cH2:1])[cH2:5]>CC(=O)O>n([cH:4][cH:3][cH:2][cH2:1])[cH2:5]')

        rs = conn.execute(
            select([func.reaction_from_smarts('C(F)(F)F.[c1:1][c:2][c:3][c:4]c[c1:5]>CC(=O)O>[c1:1][c:2][c:3][c:4]n[c1:5]')])
            )
        self.assertEqual(rs.fetchall()[0][0], 'c([cH:4][cH:3][cH:2][cH2:1])[cH2:5]>CC(=O)O.FC(F)F>n([cH:4][cH:3][cH:2][cH2:1])[cH2:5]')

        rs = conn.execute(
            select([func.reaction_from_smarts('c1ccc[n,c]c1>>c1nccnc1')])
            )
        self.assertEqual(rs.fetchall()[0][0], 'c1ccncc1>>c1cnccn1')

        rs = conn.execute(
            select([func.reaction_to_smiles(func.reaction_from_smiles('c1ccccc1>>c1cccnc1'))])
            )
        self.assertEqual(rs.fetchall()[0][0], 'c1ccccc1>>c1ccncc1')
