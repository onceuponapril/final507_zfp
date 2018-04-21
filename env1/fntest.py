import unittest
from fn import *


class TestYelpData(unittest.TestCase):
    def test_yelp_data(self):
        DBNAME='test.sqlite'
        conn = sqlite3.connect(DBNAME,check_same_thread=False)
        cur = conn.cursor()

        statement = '''
                DROP TABLE IF EXISTS 'EAT';
            '''
        cur.execute(statement)
        conn.commit()

        statement = '''
                DROP TABLE IF EXISTS 'RIDE';
            '''
        cur.execute(statement)
        conn.commit()
        eat_tb=create_first_table(DBNAME)


        headers_eat=cur.execute('SELECT * FROM EAT').description
        headers_ride=cur.execute('SELECT * FROM RIDE').description

        self.assertEqual(headers_eat[1][0],'City')
        self.assertEqual(headers_eat[-1][0],'address')
        self.assertEqual(headers_ride[1][0],'Origin')
        self.assertEqual(headers_ride[-1][0],'EAT_ID')



        yelpdt=Yelpeat('Ann Arbor',DBNAME).create_db()

        statement="SELECT * FROM EAT WHERE City='{}'".format("Ann Arbor")
        results=cur.execute(statement).fetchone()
        self.assertEqual(results[1],'Ann Arbor' )
        self.assertEqual(results[2],'Frita Batidos')
        self.assertEqual(results[3],'$$')
        self.assertEqual(results[4],4)
        self.assertTrue("117" in results[5])

        sql = 'SELECT City FROM EAT'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn( ('Ann Arbor',), result_list)

        sql = '''
            SELECT Price,Rating,Address
            FROM EAT
            WHERE Name="TK Wu"
        '''
        results = cur.execute(sql)
        result_list = results.fetchone()
        self.assertEqual(result_list[0],'$$' )
        self.assertEqual(result_list[1],3.5)

        conn.close()

class TestLyftData(unittest.TestCase):

    def test_google_lyft(self):
        resultA=google_map('Time square, new york')
        resultB=google_map('Uva,new york')

        self.assertEqual(resultA,'40.759011,-73.9844722')
        self.assertEqual(resultB, '40.7721092,-73.955637')

        lyft_result=lyft_data().estmate_cost(resultA,resultB)
        self.assertIs(type(lyft_result['start']),str)


    def test_lyft(self):
        DBNAME='test.sqlite'
        conn = sqlite3.connect(DBNAME,check_same_thread=False)
        cur = conn.cursor()

        lyft_result=lyft_data().create_table('Time square, new york',['1','2'],'test.sqlite')

        self.assertEqual(lyft_result[0][1],'Time square, new york' )
        self.assertEqual(lyft_result[0][2],'40.759011,-73.9844722')

        lyft_result=lyft_data().create_table('North quad, Ann Arbor',['1','2'],'test.sqlite')





unittest.main(verbosity=4)
