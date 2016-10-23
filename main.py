from flask import Flask, render_template, request, redirect, url_for
from google.appengine.ext import ndb
import Queue
app = Flask(__name__)


@app.route('/')
def index():
    g = Gift.query().fetch()
    giftes = {}

    for gift in g:
        if gift.year in giftes:
            giftes[gift.year].append(gift)
        else:
            giftes[gift.year] = [gift]

    sorted(giftes)

    return render_template('index.html', giftes = giftes)


@app.route('/add_person', methods=["POST"])
def add_person():
    name = request.form['name']
    email = request.form['email']

    person = Person()
    person.email = email
    person.name = name
    person.put()

    return redirect(url_for('index'))

@app.route('/make_new_wheel', methods=["POST"])
def make_new_wheel():
    year = request.form['year']
    circle = generate_circel()

    for c in circle:
        gift = Gift()
        gift.personFrom = c
        gift.personTo = circle[c]
        gift.year = year
        gift.put()

    return redirect(url_for('index'))


def generate_circel():
    allGifts = Gift.query().fetch()
    tmp = Person.query().fetch()
    people = [p.name for p in tmp]
    tmpResult = dict.fromkeys(people, [])

    # Make people lists
    for p in people:
        amount = dict.fromkeys(people, 0)
        del amount[p]
        for g in allGifts:
            if g.personFrom == p:
                amount[g.personTo] += 1

        # find the once that a person have given fewest gifts
        min_val = min(amount.itervalues())
        tmpResult[p] = [k for k, v in amount.iteritems() if v == min_val]

    # Find best candidates
    result = findBestMatch(tmpResult)

    return result

def findBestMatch(ppl):
    q = Queue.Queue()
    [q.put(p) for p in ppl]
    found = dict.fromkeys(ppl, False)
    result = dict.fromkeys(ppl, None)

    while not all(value == True for value in found.values()):
        from_name = q.get()
        to_name = ppl[from_name].pop()
        if found[to_name]:
            if not len(ppl[from_name]) == 0:
                q.put(from_name)
        else:
            found[to_name] = True
            result[from_name] = to_name

    return result



class Gift(ndb.Model):
    year = ndb.StringProperty()
    personFrom = ndb.StringProperty()
    personTo = ndb.StringProperty()


class Person(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()


if __name__ == '__main__':
    app.run()
