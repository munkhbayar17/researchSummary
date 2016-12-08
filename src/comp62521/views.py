from comp62521 import app
from database import database
from flask import (render_template, request)

def format_data(data):
    fmt = "%.2f"
    result = []
    for item in data:
        if type(item) is list:
            result.append(", ".join([ (fmt % i).rstrip('0').rstrip('.') for i in item ]))
        else:
            result.append((fmt % item).rstrip('0').rstrip('.'))
    return result

@app.route("/averages")
def showAverages():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"averages"}
    args['title'] = "Averaged Data"
    tables = []
    headers = ["Average", "Conference Paper", "Journal", "Book", "Book Chapter", "All Publications"]
    averages = [ database.Stat.MEAN, database.Stat.MEDIAN, database.Stat.MODE ]
    tables.append({
        "id":1,
        "title":"Average Authors per Publication",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_per_publication(i)[1])
                for i in averages ] })
    tables.append({
        "id":2,
        "title":"Average Publications per Author",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_per_author(i)[1])
                for i in averages ] })
    tables.append({
        "id":3,
        "title":"Average Publications in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_in_a_year(i)[1])
                for i in averages ] })
    tables.append({
        "id":4,
        "title":"Average Authors in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_in_a_year(i)[1])
                for i in averages ] })

    args['tables'] = tables
    return render_template("averages.html", args=args)

@app.route("/coauthors")
def showCoAuthors():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters", "All Publications"]
    args = {"dataset":dataset, "id":"coauthors"}
    args["title"] = "Co-Authors"
    args["mapping"] = {"Author":"author","Co-Authors":"coauthors"}
    args["descending"] = {"author":0,"coauthors":0}

    key_name = ""
    if request.args.has_key('key_name'):
        key_name = request.args['key_name']
    descending = 0
    if request.args.has_key('descending'):
        descending = int(request.args['descending'])
    if request.args.has_key('key_name'):
        args["descending"][key_name] = 1-descending

    start_year = db.min_year
    if "start_year" in request.args:
        start_year = int(request.args.get("start_year"))

    end_year = db.max_year
    if "end_year" in request.args:
        end_year = int(request.args.get("end_year"))

    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))

    args["data"] = db.get_coauthor_data(start_year, end_year, pub_type, key_name, descending)
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_type"] = pub_type
    args["min_year"] = db.min_year
    args["max_year"] = db.max_year
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_str"] = PUB_TYPES[pub_type]
    return render_template("coauthors.html", args=args)

@app.route("/")
def showStatisticsMenu():
    dataset = app.config['DATASET']
    args = {"dataset":dataset}
    return render_template('index.html', args=args)
@app.route("/index")
def indexPage():
    dataset = app.config['DATASET']
    args = {"dataset":dataset}
    return render_template('index.html', args=args)

@app.route("/statisticsdetails/<status>")
def showPublicationSummary(status):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":status}
    args["mapping"] = {"Author":"author","Year":"year","Number of conference papers":"conference","Number of journals":"journals","Number of books":"books","Number of book chapters":"chapters","Total":"total","Details":"details","Conference Paper":"conferencepaper","Journal":"journal","Book":"book","Book Chapter":"bookchapter"}
    args["descending"] = {"author":0,"year":0,"conference":0,"journals":0,"books":0,"chapters":0,"total":0,"details":0,"conferencepaper":0,"journal":0,"book":0,"bookchapter":0}
    key_name = ""
    if request.args.has_key('key_name'):
        key_name = request.args['key_name']
    descending = 0
    if request.args.has_key('descending'):
        descending = int(request.args['descending'])
    if request.args.has_key('key_name'):
        args["descending"][key_name] = 1-descending
    if (status == "publication_summary"):
        args["title"] = "Publication Summary"
        args["data"] = db.get_publication_summary(key_name,descending)
        return render_template('statistics_details_sortable.html', args=args)
    elif (status == "publication_author"):
        args["title"] = "Author Publication"
        args["data"] = db.get_publications_by_author(key_name, descending)
        return render_template('statistics_details_author.html', args=args)
    elif (status == "publication_year"):
        args["title"] = "Publication by Year"
        args["data"] = db.get_publications_by_year(key_name, descending)
        return render_template('statistics_details_sortable.html', args=args)
    elif (status == "author_year"):
        args["title"] = "Author by Year"
        args["data"] = db.get_author_totals_by_year()
        return render_template('statistics_details.html', args=args)
    return None

@app.route("/stats")
def showStats():
    dataset=app.config['DATASET']
    db=app.config['DATABASE']
    args={"dataset":dataset,"id":"stats"}
    args["title"] = "Stats for Author"
    #sorting attributes
    args["mapping"] = {"Author":"author","Year":"year","Number of conference papers":"conference","Number of journals":"journals","Number of books":"books","Number of book chapters":"chapters","Total":"total","Details":"details","Conference Paper":"conferencepaper","Journal":"journal","Book":"book","Book Chapter":"bookchapter",
    "Publications":"total", "Conference Papers":"conference", "Journal Articles":"journals", "Book Chapters":"chapters", "Books":"books", "Co-Authors":"coauthor", "First Author":"first", "Last Author":"last","Sole Author":"sole"}
    args["descending"] = {"author":0,"year":0,"conference":0,"journals":0,"books":0,"chapters":0,"total":0,"details":0,"conferencepaper":0,"journal":0,"book":0,"bookchapter":0,"coauthor":0,"first":0,"last":0,"sole":0}
    key_name = ""
    if request.args.has_key('key_name'):
        key_name = request.args['key_name']
    descending = 0
    if request.args.has_key('descending'):
        descending = int(request.args['descending'])
    if request.args.has_key('key_name'):
        args["descending"][key_name] = 1-descending
    #searching attributes
    author_name = ""
    if request.args.has_key('author_name'):
        author_name = request.args['author_name']
    args["data"]=db.get_stats_for_author(author_name, key_name, descending)
    args["author_name"] = author_name
    return render_template('stats_for_author.html',args=args)

@app.route("/dstats")
def showDstats():
    dataset=app.config['DATASET']
    db=app.config['DATABASE']
    args={"dataset":dataset,"id":"stats"}
    args["title"] = "Stats for Author"
    #sorting attributes
    args["mapping"] = {"Author":"author","Year":"year","Number of conference papers":"conference","Number of journals":"journals","Number of books":"books","Number of book chapters":"chapters","Total":"total","Details":"details","Conference Paper":"conferencepaper","Journal":"journal","Book":"book","Book Chapter":"bookchapter",
    "Publications":"total", "Conference Papers":"conference", "Journal Articles":"journals", "Book Chapters":"chapters", "Books":"books", "Co-Authors":"coauthor", "First Author":"first", "Last Author":"last","Sole Author":"sole", "Publication Type": "pubtype"}
    args["descending"] = {"author":0,"year":0,"conference":0,"journals":0,"books":0,"chapters":0,"total":0,"details":0,"conferencepaper":0,"journal":0,"book":0,"bookchapter":0,"coauthor":0,"first":0,"last":0,"sole":0, "pubtype":0}
    key_name = ""
    if request.args.has_key('key_name'):
        key_name = request.args['key_name']
    descending = 0
    if request.args.has_key('descending'):
        descending = int(request.args['descending'])
    if request.args.has_key('key_name'):
        args["descending"][key_name] = 1-descending
    #searching attributes
    author_name = ""
    if request.args.has_key('author_name'):
        author_name = request.args['author_name']
    args["data"]=db.get_dstats_for_author(author_name, key_name, descending)
    args["author_name"] = author_name
    return render_template('stats_for_author.html',args=args)

@app.route("/name/<name>")
def showNewPage(name):
        Test = "("
        if Test in name:
            a=[]
            b=[]
            c=[]
            a=name.split(" ")
            a.pop(-1)
            b=a
            name=" ".join(b)
        dataset = app.config['DATASET']
        db = app.config['DATABASE']
        args = {"dataset":dataset, "id":name}
        args['title'] = name + " Stats:"
        tables = []
        headers = ["overall","journal articles","conference papers","books","book chapters"]
        headers2 = ["","overall","journal articles","conference papers","books","book chapters"]
        data1 = db.get_authors_pages_publications(name)
        data2 = db.get_authors_pages_first_author(name)
        Data2 = []
        Data2.append("First author")
        for i in range(0,5):
            Data2.append(data2[i])
        data3 = db.get_authors_pages_last_author(name)
        Data3 = []
        Data3.append("Last author")
        for i in range(0,5):
            Data3.append(data3[i])
        data4 = db.get_authors_pages_sole_author(name)
        Data4 = []
        Data4.append("Sole author")
        for i in range(0,5):
            Data4.append(data4[i])
        data5 = db.get_authors_pages_coauthors(name)
        tables.append({
            "id":1,
            "title":"Summary",
            "header":headers2,
            "rows":[ Data4,Data2,Data3 ]
                })
        tables.append({
            "id":2,
            "title":"Number of publications",
            "header":headers,
            "rows":[ data1 ]
                })
        tables.append({
            "id":3,
            "title":"Number of times first author",
            "header":headers,
            "rows":[ data2 ] })
        tables.append({
            "id":4,
            "title":"Number of times last author",
            "header":headers,
            "rows":[ data3 ] })
        tables.append({
            "id":5,
            "title":"Number of times sole author",
            "header":headers,
            "rows":[ data4 ] })
        args['tables'] = tables

        title1 = "Number of co-authors"
        raws =data5

        return render_template("authors_page.html", args=args,raws=raws,title1=title1)


@app.route("/degrees")
def showDegrees():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset}
    dataset = app.config['DATASET']
    args = {"dataset":dataset}
    args['title'] = "Degrees_of_Separation"
    author_name_1 = ""
    author_name_2 = ""
    if request.args.has_key('author_name_1'):
        author_name_1 = request.args['author_name_1']
    if request.args.has_key('author_name_2'):
        author_name_2 = request.args['author_name_2']
    args["author_name_1"] = author_name_1
    args["author_name_2"] = author_name_2
    if len(author_name_1) > 0 and len(author_name_2) > 0:
        R = []
        t = 0
        M = []
        args["data"] = db.degrees_of_separation(author_name_1,author_name_2,t,R,M)
    else:
        args["data"] = db.return_null()
    return render_template("degrees_of_separation.html",args=args)
