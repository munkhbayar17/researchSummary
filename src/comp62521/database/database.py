from comp62521.statistics import average
import itertools
import numpy as np
from xml.sax import handler, make_parser, SAXException

PublicationType = ["Conference Paper", "Journal", "Book", "Book Chapter"]

class Publication:
    CONFERENCE_PAPER = 0
    JOURNAL = 1
    BOOK = 2
    BOOK_CHAPTER = 3

    def __init__(self, pub_type, title, year, authors):
        self.pub_type = pub_type
        self.title = title
        if year:
            self.year = int(year)
        else:
            self.year = -1
        self.authors = authors

class Author:
    soloPublishCount = 0
    firstAuthorCount = 0
    lastAuthorCount = 0
    publishCount = 0
    confPaperCount = 0
    journalArtCount = 0
    bookChapterCount = 0
    bookCount = 0
    coAuthorCount = 0
    id = -1

    def __init__(self, name):
        self.name = name
        self.soloPublishCount = 0
        self.firstAuthorCount = 0
        self.lastAuthorCount = 0
        self.publishCount = 0
        self.confPaperCount = 0
        self.journalArtCount = 0
        self.bookChapterCount = 0
        self.bookCount = 0
        self.coAuthorCount = 0
        self.id = -1

class Stat:
    STR = ["Mean", "Median", "Mode"]
    FUNC = [average.mean, average.median, average.mode]
    MEAN = 0
    MEDIAN = 1
    MODE = 2

class Database:
    def read(self, filename):
        self.publications = []
        self.authors = []
        self.author_idx = {}
        self.min_year = None
        self.max_year = None

        handler = DocumentHandler(self)
        parser = make_parser()
        parser.setContentHandler(handler)
        infile = open(filename, "r")
        valid = True
        try:
            parser.parse(infile)
        except SAXException as e:
            valid = False
            print "Error reading file (" + e.getMessage() + ")"
        infile.close()

        for p in self.publications:
            if self.min_year == None or p.year < self.min_year:
                self.min_year = p.year
            if self.max_year == None or p.year > self.max_year:
                self.max_year = p.year

        return valid

    def get_all_authors(self):
        return self.author_idx.keys()

    def get_coauthor_data(self, start_year, end_year, pub_type, key_name="", descending=0):
        coauthors = {}
        for p in self.publications:
            if ((start_year == None or p.year >= start_year) and
                (end_year == None or p.year <= end_year) and
                (pub_type == 4 or pub_type == p.pub_type)):
                for a in p.authors:
                    for a2 in p.authors:
                        if a != a2:
                            try:
                                coauthors[a].add(a2)
                            except KeyError:
                                coauthors[a] = set([a2])
        def display(db, coauthors, author_id):
            return "%s (%d)" % (db.authors[author_id].name, len(coauthors[author_id]))

        header = ("Author", "Co-Authors")
        data = []
        for a in coauthors:
            data.append([ display(self, coauthors, a),
                ", ".join([
                    display(self, coauthors, ca) for ca in coauthors[a] ]) ])

        def get_author(x):
            temp=x[0].split(' ')
            return (temp[len(temp)-2],' '.join(temp[0:len(temp)-2]))
        def get_coauthors(x):
            temp=x[0].split(' ')
            return (x[1],temp[len(temp)-2],' '.join(temp[0:len(temp)-2]))
        key_array={"author":get_author, "coauthors":get_coauthors}

        if key_name != "":
            data.sort(key=key_array[key_name], reverse=descending)

        return (header, data)

    def get_average_authors_per_publication(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ func(auth_per_pub[i]) for i in np.arange(4) ] + [ func(list(itertools.chain(*auth_per_pub))) ]
        return (header, data)

    def get_average_publications_per_author(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))

        for p in self.publications:
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(pub_per_auth[:, i]) for i in np.arange(4) ] + [ func(pub_per_auth.sum(axis=1)) ]
        return (header, data)

    def get_average_publications_in_a_year(self, av):
        header = ("Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        ystats = np.zeros((int(self.max_year) - int(self.min_year) + 1, 4))

        for p in self.publications:
            ystats[p.year - self.min_year][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(4) ] + [ func(ystats.sum(axis=1)) ]
        return (header, data)

    def get_average_authors_in_a_year(self, av):
        header = ("Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        yauth = [ [set(), set(), set(), set(), set()] for _ in range(int(self.min_year), int(self.max_year) + 1) ]

        for p in self.publications:
            for a in p.authors:
                yauth[p.year - self.min_year][p.pub_type].add(a)
                yauth[p.year - self.min_year][4].add(a)

        ystats = np.array([ [ len(S) for S in y ] for y in yauth ])

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(5) ]
        return (header, data)

    def get_publication_summary_average(self, av):
        header = ("Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))
        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        name = Stat.STR[av]
        func = Stat.FUNC[av]

        data = [
            [name + " authors per publication"]
                + [ func(auth_per_pub[i]) for i in np.arange(4) ]
                + [ func(list(itertools.chain(*auth_per_pub))) ],
            [name + " publications per author"]
                + [ func(pub_per_auth[:, i]) for i in np.arange(4) ]
                + [ func(pub_per_auth.sum(axis=1)) ] ]
        return (header, data)

    def get_publication_summary(self, key_name="", descending=0):
        header = ("Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "Total")

        plist = [0, 0, 0, 0]
        alist = [set(), set(), set(), set()]

        for p in self.publications:
            plist[p.pub_type] += 1
            for a in p.authors:
                alist[p.pub_type].add(a)
        # create union of all authors
        ua = alist[0] | alist[1] | alist[2] | alist[3]

	def get_details(x):
	    return x[0]
	def get_conferencepaper(x):
	    return x[1]
	def get_journal(x):
	    return x[2]
	def get_book(x):
	    return x[3]
	def get_bookchapter(x):
	    return x[4]
	def get_total(x):
	    return x[5]
	key_array={"details":get_details, "conferencepaper":get_conferencepaper, "journal":get_journal, "book":get_book, "bookchapter":get_bookchapter, "total":get_total}

        data = [
            ["Number of publications"] + plist + [sum(plist)],
            ["Number of authors"] + [ len(a) for a in alist ] + [len(ua)] ]

	if key_name != "":
            data.sort(key=key_array[key_name], reverse=descending)
        return (header, data)

    def get_average_authors_per_publication_by_author(self, av):
        header = ("Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapters", "All publications")

        astats = [ [[], [], [], []] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [self.authors[i].name]
            + [ func(L) for L in astats[i] ]
            + [ func(list(itertools.chain(*astats[i]))) ]
            for i in range(len(astats)) ]
        return (header, data)


    def get_publications_by_author(self, key_name="", descending=0):
        header = ("Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapters", "Total")

        astats = [ [0, 0, 0, 0] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type] += 1

        def get_author(x):
            temp=x[0].split(' ')
            return (temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_papers(x):
            temp=x[0].split(' ')
            return (x[1],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_journals(x):
            temp=x[0].split(' ')
            return (x[2],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_books(x):
            temp=x[0].split(' ')
            return (x[3],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_chapters(x):
            temp=x[0].split(' ')
            return (x[4],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_total(x):
            temp=x[0].split(' ')
            return (x[5],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        key_array={"author":get_author, "conference":get_papers, "journals":get_journals, "books":get_books, "chapters":get_chapters, "total":get_total}

        data = [ [self.authors[i].name] + astats[i] + [sum(astats[i])]
            for i in range(len(astats)) ]
        if key_name != "":
            data.sort(key=key_array[key_name], reverse=descending)
        return (header, data)

    def get_average_authors_per_publication_by_year(self, av):
        header = ("Year", "Conference papers",
            "Journals", "Books",
            "Book chapters", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type].append(len(p.authors))
            except KeyError:
                ystats[p.year] = [[], [], [], []]
                ystats[p.year][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(L) for L in ystats[y] ]
            + [ func(list(itertools.chain(*ystats[y]))) ]
            for y in ystats ]
        return (header, data)

    def get_publications_by_year(self, key_name="", descending=0):
        header = ("Year", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapters", "Total")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type] += 1
            except KeyError:
                ystats[p.year] = [0, 0, 0, 0]
                ystats[p.year][p.pub_type] += 1

        def get_year(x):
            return x[0]
        def get_papers(x):
            return x[1]
        def get_journals(x):
            return x[2]
        def get_books(x):
            return x[3]
        def get_chapters(x):
            return x[4]
        def get_total(x):
            return x[5]
        key_array={"year":get_year, "conference":get_papers, "journals":get_journals, "books":get_books, "chapters":get_chapters, "total":get_total}

        data = [ [y] + ystats[y] + [sum(ystats[y])] for y in ystats ]
        if key_name != "":
            data.sort(key=key_array[key_name], reverse=descending)
        return (header, data)

    def get_average_publications_per_author_by_year(self, av):
        header = ("Year", "Conference papers",
            "Journals", "Books",
            "Book chapters", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year]
            except KeyError:
                s = np.zeros((len(self.authors), 4))
                ystats[p.year] = s
            for a in p.authors:
                s[a][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(ystats[y][:, i]) for i in np.arange(4) ]
            + [ func(ystats[y].sum(axis=1)) ]
            for y in ystats ]
        return (header, data)

    def get_author_totals_by_year(self):
        header = ("Year", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year][p.pub_type]
            except KeyError:
                ystats[p.year] = [set(), set(), set(), set()]
                s = ystats[p.year][p.pub_type]
            for a in p.authors:
                s.add(a)
        data = [ [y] + [len(s) for s in ystats[y]] + [len(ystats[y][0] | ystats[y][1] | ystats[y][2] | ystats[y][3])]
            for y in ystats ]
        return (header, data)

    def add_publication(self, pub_type, title, year, authors):
        if year == None or len(authors) == 0:
            print "Warning: excluding publication due to missing information"
            print "    Publication type:", PublicationType[pub_type]
            print "    Title:", title
            print "    Year:", year
            print "    Authors:", ",".join(authors)
            return
        if title == None:
            print "Warning: adding publication with missing title [ %s %s (%s) ]" % (PublicationType[pub_type], year, ",".join(authors))
        idlist = []
        for a in authors:
            try:
                idlist.append(self.author_idx[a])
            except KeyError:
                a_id = len(self.authors)
                self.author_idx[a] = a_id
                idlist.append(a_id)
                self.authors.append(Author(a))
        self.publications.append(
            Publication(pub_type, title, year, idlist))
        if (len(self.publications) % 100000) == 0:
            print "Adding publication number %d (number of authors is %d)" % (len(self.publications), len(self.authors))

        if self.min_year == None or year < self.min_year:
            self.min_year = year
        if self.max_year == None or year > self.max_year:
            self.max_year = year

    def _get_collaborations(self, author_id, include_self):
        data = {}
        for p in self.publications:
            if author_id in p.authors:
                for a in p.authors:
                    try:
                        data[a] += 1
                    except KeyError:
                        data[a] = 1
        if not include_self:
            del data[author_id]
        return data

    def get_coauthor_details(self, name):
        author_id = self.author_idx[name]
        data = self._get_collaborations(author_id, True)
        return [ (self.authors[key].name, data[key])
            for key in data ]

    def get_network_data(self):
        na = len(self.authors)

        nodes = [ [self.authors[i].name, -1] for i in range(na) ]
        links = set()
        for a in range(na):
            collab = self._get_collaborations(a, False)
            nodes[a][1] = len(collab)
            for a2 in collab:
                if a < a2:
                    links.add((a, a2))
        return (nodes, links)

    def get_stats_for_author(self, author_name, key_name, descending):
        header=("Author", "Publications", "Conference Papers", "Journal Articles", "Books","Book Chapters",
        "Co-Authors", "First Author", "Last Author", "Sole Author")
        data=[]
        publics = []
        #filtering authors
        authors = self.find_authors(author_name)
        #filtering author by name
        for a in authors:
            #init author
            a.soloPublishCount = 0
            a.firstAuthorCount = 0
            a.lastAuthorCount = 0
            a.publishCount = 0
            a.confPaperCount = 0
            a.journalArtCount = 0
            a.bookChapterCount = 0
            a.bookCount = 0
            a.coAuthorCount = 0
            a.id = self.author_idx[a.name]
            coauthors = []
            for p in self.publications:
                #print p.authors
                if a.id in p.authors:
                    #co-authors
                    for c in p.authors:
                        if c not in coauthors:
                            coauthors.append(c)
                    a.coAuthorCount = len(coauthors) - 1
                    #solo
                    if len(p.authors) == 1:
                        a.soloPublishCount += 1
                    #first
                    else:
                        if p.authors[0] == a.id:
                            a.firstAuthorCount += 1
                        else:
                            if p.authors[-1] == a.id:#last
                                a.lastAuthorCount += 1
                    #pub_type
                    a.publishCount += 1
                    if p.pub_type == 0:
                        a.confPaperCount += 1
                    elif p.pub_type == 1:
                        a.journalArtCount += 1
                    elif p.pub_type == 2:
                        a.bookCount += 1
                    elif p.pub_type == 3:
                        a.bookChapterCount += 1
            print a.id
            data.append((a.name, a.publishCount, a.confPaperCount, a.journalArtCount, a.bookCount, a.bookChapterCount,
            a.coAuthorCount, a.firstAuthorCount, a.lastAuthorCount, a.soloPublishCount))

        def get_author(x):
            temp = x[0].split(' ')
            return (temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_total(x):
            temp = x[0].split(' ')
            return (x[1],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_papers(x):
            temp = x[0].split(' ')
            return (x[2],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_journals(x):
            temp = x[0].split(' ')
            return (x[3],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_chapters(x):
            temp = x[0].split(' ')
            return (x[4],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_books(x):
            temp = x[0].split(' ')
            return (x[5],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_coauthor(x):
            temp = x[0].split(' ')
            return (x[6],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_first(x):
            temp = x[0].split(' ')
            return (x[7],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_last(x):
            temp = x[0].split(' ')
            return (x[8],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        def get_sole(x):
            temp = x[0].split(' ')
            return (x[9],temp[len(temp)-1],' '.join(temp[0:len(temp)-1]))
        key_array={"author":get_author, "conference":get_papers, "journals":get_journals, "books":get_books, "chapters":get_chapters, "total":get_total, "coauthor":get_coauthor, "first":get_first, "last":get_last, "sole": get_sole}
        if key_name != "":
            data.sort(key=(key_array[key_name]), reverse=int(descending))
        return(header,data)

    def find_authors(self, author_name):
        if (author_name is None) | (author_name == ""):
            return self.authors
        else:
            authors = []
            for a in self.authors:
                if author_name.lower() in a.name.lower():
                    authors.append(a)
            return authors

    def get_authors_pages_publications(self,name):
        PUcount = 0
        PUjournalArtCount = 0
        PUconfPaperCount = 0
        PUbookCount = 0
        PUbookChapterCount = 0
        id_PUauthor=self.author_idx[name]
        for p in self.publications:
            if id_PUauthor in p.authors:
                PUcount += 1
                if p.pub_type == 0:
                    PUconfPaperCount += 1
                elif p.pub_type == 1:
                    PUjournalArtCount += 1
                elif p.pub_type == 2:
                    PUbookCount += 1
                elif p.pub_type == 3:
                    PUbookChapterCount += 1
        data = [PUcount, PUjournalArtCount,  PUconfPaperCount, PUbookCount, PUbookChapterCount]
        return data

    def get_authors_pages_first_author(self,name):
        FAcount = 0
        FAjournalArtCount = 0
        FAconfPaperCount = 0
        FAbookCount = 0
        FAbookChapterCount = 0

        id_FAauthor = self.author_idx[name]
        for p in self.publications:
            if id_FAauthor in p.authors:
                if len(p.authors) != 1:
                    if id_FAauthor==p.authors[0]:
                        FAcount += 1
                        if p.pub_type == 0:
                            FAconfPaperCount += 1
                        elif p.pub_type == 1:
                            FAjournalArtCount += 1
                        elif p.pub_type == 2:
                            FAbookCount += 1
                        elif p.pub_type == 3:
                            FAbookChapterCount += 1

        data = [FAcount, FAjournalArtCount,  FAconfPaperCount, FAbookCount, FAbookChapterCount]
        return data

    def get_authors_pages_last_author(self,name):
        LAcount = 0
        LAjournalArtCount = 0
        LAconfPaperCount = 0
        LAbookCount = 0
        LAbookChapterCount = 0

        id_LAauthor = self.author_idx[name]
        for p in self.publications:
            if id_LAauthor in p.authors:
                if len(p.authors) != 1:
                    if id_LAauthor==p.authors[-1]:
                        LAcount += 1
                        if p.pub_type == 0:
                            LAconfPaperCount += 1
                        elif p.pub_type == 1:
                            LAjournalArtCount += 1
                        elif p.pub_type == 2:
                            LAbookCount += 1
                        elif p.pub_type == 3:
                            LAbookChapterCount += 1

        data = [LAcount, LAjournalArtCount,  LAconfPaperCount, LAbookCount, LAbookChapterCount]
        return data

    def get_authors_pages_sole_author(self, name):
        SAcount = 0
        SAjournalArtCount = 0
        SAconfPaperCount = 0
        SAbookCount = 0
        SAbookChapterCount = 0

        id_SAauthor = self.author_idx[name]
        for p in self.publications:
            if id_SAauthor in p.authors:
                if len(p.authors) == 1:
                    SAcount += 1
                    if p.pub_type == 0:
                        SAconfPaperCount += 1
                    elif p.pub_type == 1:
                        SAjournalArtCount += 1
                    elif p.pub_type == 2:
                        SAbookCount += 1
                    elif p.pub_type == 3:
                        SAbookChapterCount += 1

        data = [SAcount, SAjournalArtCount,  SAconfPaperCount, SAbookCount, SAbookChapterCount]
        return data

    def get_authors_pages_coauthors(self,name):
        CAcount = 0
        CA=[]

        id_CAauthor = self.author_idx[name]
        for p in self.publications:
            if id_CAauthor in p.authors and len(p.authors) != 1:
                for C in p.authors:
                    if C not in CA:
                        CA.append(C)
        CAcount = len(CA) - 1
        data = CAcount
        return data


    def judge_number_name(self,nameX):
        if type(nameX) == type(1):
            x = nameX
        else:
            x = self.author_idx[nameX]
        return x

    def degrees_of_separation(self,authorA,authorB,t,R,M):
        authorA_id = self.judge_number_name(authorA)
        authorB_id = self.judge_number_name(authorB)
        New = []
        R.append(authorA_id)
        for p in self.publications:
            if authorA_id in p.authors:
                for i in p.authors:
                    if i not in R:
                        New.append(i)
        New = list(set(New))
        if len(New) == 0:
            return None
        else:
            if authorB_id in New:
                M.append(t)
            else:
                t = t+1
                for j in New:
                    self.degrees_of_separation(j,authorB_id,t,R,M)
        if len(M) != 0:
            k = min(M)
        else: k = "X"
        header = ("Author 1", "Author 2", "Degrees_of_Separation")
        data = []
        data.append((authorA ,authorB ,k))
        return (header, data)

    def return_null(self):
        header = ("Author 1", "Author 2", "Degrees_of_Separation")
        data = []
        data.append((None,None,0))
        return (header, data)

class DocumentHandler(handler.ContentHandler):
    TITLE_TAGS = [ "sub", "sup", "i", "tt", "ref" ]
    PUB_TYPE = {
        "inproceedings":Publication.CONFERENCE_PAPER,
        "article":Publication.JOURNAL,
        "book":Publication.BOOK,
        "incollection":Publication.BOOK_CHAPTER }

    def __init__(self, db):
        self.tag = None
        self.chrs = ""
        self.clearData()
        self.db = db

    def clearData(self):
        self.pub_type = None
        self.authors = []
        self.year = None
        self.title = None

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        if name in self.TITLE_TAGS:
            return
        if name in DocumentHandler.PUB_TYPE.keys():
            self.pub_type = DocumentHandler.PUB_TYPE[name]
        self.tag = name
        self.chrs = ""

    def endElement(self, name):
        if self.pub_type == None:
            return
        if name in self.TITLE_TAGS:
            return
        d = self.chrs.strip()
        if self.tag == "author":
            self.authors.append(d)
        elif self.tag == "title":
            self.title = d
        elif self.tag == "year":
            self.year = int(d)
        elif name in DocumentHandler.PUB_TYPE.keys():
            self.db.add_publication(
                self.pub_type,
                self.title,
                self.year,
                self.authors)
            self.clearData()
        self.tag = None
        self.chrs = ""

    def characters(self, chrs):
        if self.pub_type != None:
            self.chrs += chrs
