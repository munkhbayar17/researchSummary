from os import path
import unittest

from comp62521.database import database

class TestDatabase(unittest.TestCase):

    def setUp(self):
        dir, _ = path.split(__file__)
        self.data_dir = path.join(dir, "..", "data")

    def test_read(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        self.assertEqual(len(db.publications), 1)

    def test_read_invalid_xml(self):
        db = database.Database()
        self.assertFalse(db.read(path.join(self.data_dir, "invalid_xml_file.xml")))

    def test_read_missing_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_year.xml")))
        self.assertEqual(len(db.publications), 0)

    def test_read_missing_title(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_title.xml")))
        # publications with missing titles should be added
        self.assertEqual(len(db.publications), 1)

    def test_get_average_authors_per_publication(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        _, data = db.get_average_authors_per_publication(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.3, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 2, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MODE)
        self.assertEqual(data[0], [2])

    def test_get_average_publications_per_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        _, data = db.get_average_publications_per_author(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MODE)
        self.assertEqual(data[0], [0, 1, 2, 3])

    def test_get_average_publications_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-3.xml")))
        _, data = db.get_average_publications_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.5, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [3])

    def test_get_average_authors_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-4.xml")))
        _, data = db.get_average_authors_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.8, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [0, 2, 4, 5])
        # additional test for union of authors
        self.assertEqual(data[-1], [0, 2, 4, 5])

    def test_get_publication_summary(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publication_summary()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data[0]), 6,
            "incorrect number of columns in data")
        self.assertEqual(len(data), 2,
            "incorrect number of rows in data")
        self.assertEqual(data[0][1], 1,
            "incorrect number of publications for conference papers")
        self.assertEqual(data[1][1], 2,
            "incorrect number of authors for conference papers")

    def test_get_average_authors_per_publication_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        header, data = db.get_average_authors_per_publication_by_author(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 3,
            "incorrect average of number of conference papers")
        self.assertEqual(data[0][1], 1.5,
            "incorrect mean journals for author1")
        self.assertEqual(data[1][1], 2,
            "incorrect mean journals for author2")
        self.assertEqual(data[2][1], 1,
            "incorrect mean journals for author3")

    def test_get_publications_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_author()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 2,
            "incorrect number of authors")
        self.assertEqual(data[0][-1], 1,
            "incorrect total")

    def test_get_average_publications_per_author_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_average_publications_per_author_by_year(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")

    def test_get_publications_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_year()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")

    def test_get_author_totals_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_author_totals_by_year()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")
        self.assertEqual(data[0][1], 2,
            "incorrect number of authors in result")

    def test_get_stats_for_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_stats_for_author("", "author", 0)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),2,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 1,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 1,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 0,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 0,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 1,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 1,
            "incorrect author1 count of first")
        self.assertEqual(data[0][8], 0,
            "incorrect author1 count of last author")
        self.assertEqual(data[1][1], 1,
            "incorrect author2 count of publications")
        self.assertEqual(data[1][2], 1,
            "incorrect author2 count of papers")
        self.assertEqual(data[1][3], 0,
            "incorrect author2 count of articles")
        self.assertEqual(data[1][4], 0,
            "incorrect author2 count of chapters")
        self.assertEqual(data[1][5], 0,
            "incorrect author2 count of books")
        self.assertEqual(data[1][6], 1,
            "incorrect author2 count of co-authors")
        self.assertEqual(data[1][7], 0,
            "incorrect author2 count of first author")
        self.assertEqual(data[1][8], 1,
            "incorrect author2 count of last author")

    def test_get_stats_for_author_sp2(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        header, data = db.get_stats_for_author("author3", "author", 0)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),1,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 1,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 1,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 0,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 0,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 0,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 0,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 0,
            "incorrect author1 count of last author")
        self.assertEqual(data[0][9], 1,
            "incorrect author1 count of sole author")

    def test_get_stats_for_author_sp2_2(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        header, data = db.get_stats_for_author("Stefano Ceri", "author", 0)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),1,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 218,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 100,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 94,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 6,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 18,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 230,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 78,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 25,
            "incorrect author1 count of last author")
        self.assertEqual(data[0][9], 8,
            "incorrect author1 count of sole author")

    def test_get_stats_for_author_sp2_3(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        header, data = db.get_stats_for_author("pe", "total", 1)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),12,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 7,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 4,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 2,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 1,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 6,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 0,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 1,
            "incorrect author1 count of last author")
        self.assertEqual(data[0][9], 0,
            "incorrect author1 count of sole author")

    def test_get_stats_for_author_sp2_4(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        header, data = db.get_stats_for_author("pe", "conference", 1)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),12,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 7,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 4,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 2,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 1,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 6,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 0,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 1,
            "incorrect author1 count of last author")
        self.assertEqual(data[0][9], 0,
            "incorrect author1 count of sole author")

    def test_get_stats_for_author_sp2_5(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        header, data = db.get_stats_for_author("pe", "journals", 1)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),12,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 4,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 1,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 3,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 0,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 9,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 0,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 1,
            "incorrect author1 count of last author")

    def test_get_stats_for_author_sp2_6(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        header, data = db.get_stats_for_author("pe", "chapters", 1)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),12,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 1,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 0,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 1,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 0,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 3,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 0,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 1,
            "incorrect author1 count of last author")
        self.assertEqual(data[0][9], 0,
            "incorrect author1 count of sole author")

    def test_get_stats_for_author_sp2_7(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        header, data = db.get_stats_for_author("pe", "books", 1)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),12,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 1,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 0,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 0,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 1,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 3,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 0,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 1,
            "incorrect author1 count of last author")
        self.assertEqual(data[0][9], 0,
            "incorrect author1 count of sole author")

    def test_get_stats_for_author_sp2_8(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        header, data = db.get_stats_for_author("pe", "coauthor", 0)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),12,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 1,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 0,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 1,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 0,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 2,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 1,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 0,
            "incorrect author1 count of last author")

    def test_get_stats_for_author_sp2_9(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        header, data = db.get_stats_for_author("pe", "first", 1)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),12,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 3,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 3,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 0,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 0,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 8,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 2,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 0,
            "incorrect author1 count of last author")

    def test_get_stats_for_author_sp2_10(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        header, data = db.get_stats_for_author("pe", "last", 0)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),12,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 1,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 0,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 1,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 0,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 2,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 1,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 0,
            "incorrect author1 count of last author")

    def test_get_stats_for_author_sp2_11(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        header, data = db.get_stats_for_author("pe", "coauthor", 0)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),12,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 1,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 0,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 1,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 0,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 2,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 1,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 0,
            "incorrect author1 count of last author")

    def test_get_stats_for_author_sp2_12(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_stats_for_author("", "sole", 0)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),2,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 1,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 1,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 0,
            "incorrect author1 count of articles")
        self.assertEqual(data[0][4], 0,
            "incorrect author1 count of chapters")
        self.assertEqual(data[0][5], 0,
            "incorrect author1 count of books")
        self.assertEqual(data[0][6], 1,
            "incorrect author1 count of co-authors")
        self.assertEqual(data[0][7], 1,
            "incorrect author1 count of first author")
        self.assertEqual(data[0][8], 0,
            "incorrect author1 count of last author")
        self.assertEqual(data[0][9], 0,
            "incorrect author1 count of last author")


    def test_get_stats_for_author_sp1_2(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        header, data = db.get_stats_for_author("Stefano Ceri", "author", 0)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data),1,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 218,
            "incorrect author1 count of publications")
        self.assertEqual(data[0][2], 100,
            "incorrect author1 count of papers")
        self.assertEqual(data[0][3], 94,
            "incorrect author1 count of articles")

    def test_get_publication_summary_sp1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publication_summary("conferencepaper", 1)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 2,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 2,
            "incorrect conference paper")
        self.assertEqual(data[0][2], 0,
            "incorrect journal")
        self.assertEqual(data[0][3], 0,
            "incorrect journal")
        self.assertEqual(data[0][4], 0,
            "incorrect journal")
        self.assertEqual(data[0][5], 2,
            "incorrect journal")

    def test_find_authors(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        data = db.find_authors(None)
        self.assertEqual(len(data), 2,
            "auhtors count doesn't match")

    def test_find_authors(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        self.authors = None
        data = db.find_authors(None)
        self.assertEqual(len(data), 2,
            "auhtors count doesn't match")

    def test_get_publications_by_author_sp1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_author("journals", 1)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 2,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 1,
            "incorrect conference paper")
        self.assertEqual(data[0][2], 0,
            "incorrect journal")
        self.assertEqual(data[0][3], 0,
            "incorrect journal")
        self.assertEqual(data[0][4], 0,
            "incorrect journal")
        self.assertEqual(data[0][5], 1,
            "incorrect journal")

    def test_get_publications_by_year_sp1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        header, data = db.get_publications_by_year("journals", 1)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 33,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 35,
            "incorrect conference paper")
        self.assertEqual(data[0][2], 34,
            "incorrect journal")
        self.assertEqual(data[0][3], 0,
            "incorrect journal")
        self.assertEqual(data[0][4], 2,
            "incorrect journal")
        self.assertEqual(data[0][5], 71,
            "incorrect journal")

    def test_get_publications_by_year_sp2(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_sorting_example.xml")))
        header, data = db.get_publications_by_year("journals", 1)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 5,
            "incorrect number of rows")
        self.assertEqual(data[0][1], 0,
            "incorrect conference paper")
        self.assertEqual(data[0][2], 3,
            "incorrect journal")
        self.assertEqual(data[0][3], 0,
            "incorrect journal")
        self.assertEqual(data[0][4], 1,
            "incorrect journal")
        self.assertEqual(data[0][5], 4,
            "incorrect journal")

    def test_get_authors_pages_publications_sp1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_authors_pages_publications("Yeliz Yesilada")
        self.assertEqual(data[0], 2, "incorrect overall")
        self.assertEqual(data[1], 0, "incorrect journals articles")
        self.assertEqual(data[2], 2, "incorrect conference paper")
        self.assertEqual(data[3], 0, "incorrect books")
        self.assertEqual(data[4], 0, "incorrect books chapters" )

    def test_get_authors_pages_publications_sp2(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_authors_pages_publications("Carole A. Goble")
        self.assertEqual(data[0], 3, "incorrect overall")
        self.assertEqual(data[1], 1, "incorrect journals articles")
        self.assertEqual(data[2], 2, "incorrect conference paper")
        self.assertEqual(data[3], 0, "incorrect books")
        self.assertEqual(data[4], 0, "incorrect books chapters" )

    def test_get_authors_pages_publications_sp3(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_authors_pages_publications("Piero Fraternali")
        self.assertEqual(data[0], 1, "incorrect overall")
        self.assertEqual(data[1], 0, "incorrect journals articles")
        self.assertEqual(data[2], 0, "incorrect conference paper")
        self.assertEqual(data[3], 1, "incorrect books")
        self.assertEqual(data[4], 0, "incorrect books chapters" )

    def test_get_authors_pages_publications_sp4(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        data = db.get_authors_pages_publications("Pedro Domingos")
        self.assertEqual(data[0], 7, "incorrect overall")
        self.assertEqual(data[1], 2, "incorrect journals articles")
        self.assertEqual(data[2], 4, "incorrect conference paper")
        self.assertEqual(data[3], 0, "incorrect books")
        self.assertEqual(data[4], 1, "incorrect books chapters" )


    def test_get_authors_pages_first_author_sp1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_authors_pages_first_author("Stefano Ceri")
        self.assertEqual(data[0], 2, "incorrect overall")
        self.assertEqual(data[1], 0, "incorrect journals articles")
        self.assertEqual(data[2], 0, "incorrect conference paper")
        self.assertEqual(data[3], 1, "incorrect books")
        self.assertEqual(data[4], 1, "incorrect books chapters" )

    def test_get_authors_pages_first_author_sp2(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_authors_pages_first_author("Simon Harper")
        self.assertEqual(data[0], 1, "incorrect overall")
        self.assertEqual(data[1], 0, "incorrect journals articles")
        self.assertEqual(data[2], 1, "incorrect conference paper")
        self.assertEqual(data[3], 0, "incorrect books")
        self.assertEqual(data[4], 0, "incorrect books chapters" )

    def test_get_authors_pages_first_author_sp3(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_authors_pages_first_author("Erich Bornberg-Bauer")
        self.assertEqual(data[0], 1, "incorrect overall")
        self.assertEqual(data[1], 1, "incorrect journals articles")
        self.assertEqual(data[2], 0, "incorrect conference paper")
        self.assertEqual(data[3], 0, "incorrect books")
        self.assertEqual(data[4], 0, "incorrect books chapters" )

    def test_get_authors_pages_last_author_sp1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_authors_pages_last_author("Rodrigo Lopez")
        self.assertEqual(data[0], 1, "incorrect overall")
        self.assertEqual(data[1], 1, "incorrect journals articles")
        self.assertEqual(data[2], 0, "incorrect conference paper")
        self.assertEqual(data[3], 0, "incorrect books")
        self.assertEqual(data[4], 0, "incorrect books chapters" )

    def test_get_authors_pages_last_author_sp2(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_authors_pages_last_author("Yeliz Yesilada")
        self.assertEqual(data[0], 1, "incorrect overall")
        self.assertEqual(data[1], 0, "incorrect journals articles")
        self.assertEqual(data[2], 1, "incorrect conference paper")
        self.assertEqual(data[3], 0, "incorrect books")
        self.assertEqual(data[4], 0, "incorrect books chapters" )

    def test_get_authors_pages_last_author_sp3(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_authors_pages_last_author("Piero Fraternali")
        self.assertEqual(data[0], 1, "incorrect overall")
        self.assertEqual(data[1], 0, "incorrect journals articles")
        self.assertEqual(data[2], 0, "incorrect conference paper")
        self.assertEqual(data[3], 1, "incorrect books")
        self.assertEqual(data[4], 0, "incorrect books chapters" )

    def test_get_authors_pages_last_author_sp4(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        data = db.get_authors_pages_last_author("Giuseppe Pozzi")
        self.assertEqual(data[0], 1, "incorrect overall")
        self.assertEqual(data[1], 0, "incorrect journals articles")
        self.assertEqual(data[2], 0, "incorrect conference paper")
        self.assertEqual(data[3], 0, "incorrect books")
        self.assertEqual(data[4], 1, "incorrect books chapters" )

    def test_get_authors_pages_sole_author_sp1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_authors_pages_sole_author("Robert Stevens")
        self.assertEqual(data[0], 0, "incorrect overall")
        self.assertEqual(data[1], 0, "incorrect journals articles")
        self.assertEqual(data[2], 0, "incorrect conference paper")
        self.assertEqual(data[3], 0, "incorrect books")
        self.assertEqual(data[4], 0, "incorrect books chapters" )

    def test_get_authors_pages_sole_author_sp2(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_sorting_example.xml")))
        data = db.get_authors_pages_sole_author("Alon Y. Halevy")
        self.assertEqual(data[0], 3, "incorrect overall")
        self.assertEqual(data[1], 2, "incorrect journals articles")
        self.assertEqual(data[2], 1, "incorrect conference paper")
        self.assertEqual(data[3], 0, "incorrect books")
        self.assertEqual(data[4], 0, "incorrect books chapters" )

    def test_get_authors_pages_coauthors(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_authors_pages_coauthors("Bernard Horan")
        self.assertEqual(data, 3, "incorrect co-authors")

    def test_degrees_of_separation_sp1(self):
        t = 0
        R = []
        M = []
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        header,data = db.degrees_of_separation("Sean Bechhofer","Yeliz Yesilada",t,R,M)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(data, [('Sean Bechhofer', 'Yeliz Yesilada', 0)], "incorrect degrees")

    def test_degrees_of_separation_sp2(self):
        t = 0
        R = []
        M = []
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        header,data = db.degrees_of_separation("Sean Bechhofer","Simon Harper",t,R,M)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(data, [('Sean Bechhofer', 'Simon Harper', 1)], "incorrect degrees")

    def test_degrees_of_separation_sp3(self):
        t = 0
        R = []
        M = []
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        header,data = db.degrees_of_separation("Rodrigo Lopez","Norman W. Paton",t,R,M)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(data, [('Rodrigo Lopez', 'Norman W. Paton', 'X')], "incorrect degrees")

    def test_get_coauthor_data_sp3_1(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        header,data = db.get_coauthor_data(2000,2005,4,"author",1)
        self.assertEqual(data[0][0], u'Z. Meral zsoyoglu (6)', "incorrect author")
        self.assertEqual(data[0][1], u'Stefano Ceri (79), Richard T. Snodgrass (34), Leonid A. Kalinichenko (6), Masaru Kitsuregawa (6), Hongjun Lu (6), Victor Vianu (6)', "incorrect coauthors")

if __name__ == '__main__':
    unittest.main()
