"""
Tabular editor

The TabularEditor can be used for many of the same purposes as the TableEditor,
that is, for displaying a table of attributes of lists or arrays of objects.

While similar in function, the tabular editor has advantages and disadvantages
relative to the table editor. See the Traits UI User Manual for details.

This example defines three classes:

 - *Person*: A single person.
 - *MarriedPerson*: A married person (subclass of Person).
 - *Report*: Defines a report based on a list of single and married people.

It creates a tabular display of 10,000 single and married people showing the
following information:

 - Name of the person.
 - Age of the person.
 - The person's address.
 - The name of the person's spouse (if any).

In addition:

 - It uses a Courier 10 point font for each line in the table.
 - It displays age column right, instead of left, justified.
 - If the person is a minor (age < 18) and married, it displays a red flag
   image in the age column.
 - If the person is married, it makes the background color for that row a light
   blue.
   
 - If this demo is running under QT, it displays each person's surname
   in a row label.

This example demonstrates:

 - How to set up a *TabularEditor*.
 - The display speed of the *TabularEditor*.
 - How to create a *TabularAdapter* that meets each of the specified display
   requirements.

Additional notes:

 - You can change the current selection using the up and down arrow keys.
 - You can move a selected row up and down in the table using the left and
   right arrow keys.
"""

from random import randint, choice, shuffle
from traits.api import HasTraits, Str, Int, List, Instance, Property, \
     Constant, Color
from traits.etsconfig.api import ETSConfig
from traitsui.api import View, Group, Item, TabularEditor
from traitsui.tabular_adapter import TabularAdapter

#-- Person Class Definition ----------------------------------------------------

class Person(HasTraits):

    name    = Str
    address = Str
    age     = Int
    
    # surname is displayed in qt-only row label:
    surname = Property(fget=lambda self: self.name.split()[-1], 
                       depends_on='name')

#-- MarriedPerson Class Definition ---------------------------------------------

class MarriedPerson(Person):

    partner = Instance(Person)

#-- Tabular Adapter Definition -------------------------------------------------

class ReportAdapter(TabularAdapter):
    """ The tabular adapter interfaces between the tabular editor and the data 
    being displayed. For more details, please refer to the traitsUI user guide. 
    """
    # List of (Column labels, Column ID).
    columns = [ ('Name',    'name'),
                ('Age',     'age'),
                ('Address', 'address'),
                ('Spouse',  'spouse') ]

    row_label_name = 'surname'

    # Interfacing between the model and the view: make some of the cell 
    # attributes a property whose behavior is then controlled by the get 
    # (and optionally set methods). The cell is identified by its column 
    # ID (age, spouse).
    
    # Font fails with wx in OSX; see traitsui issue #13:
    # font                      = 'Courier 10'
    age_alignment             = Constant('right')
    MarriedPerson_age_image   = Property
    MarriedPerson_bg_color    = Color(0xE0E0FF)
    MarriedPerson_spouse_text = Property
    Person_spouse_text        = Constant('')

    def _get_MarriedPerson_age_image(self):
        if self.item.age < 18:
            return '@icons:red_ball'

        return None

    def _get_MarriedPerson_spouse_text(self):
        return self.item.partner.name

#-- Tabular Editor Definition --------------------------------------------------

# The tabular editor works in conjunction with an adapter class, derived from 
# TabularAdapter. 
tabular_editor = TabularEditor(
    adapter    = ReportAdapter(),
    operations = [ 'move', 'edit' ],
    # Row titles are not supported in WX:
    show_row_titles = ETSConfig.toolkit == 'qt4',
)

#-- Report Class Definition ----------------------------------------------------

class Report(HasTraits):

    people = List(Person)

    view = View(
        Group(
            Item('people', id = 'table', editor = tabular_editor),
            show_labels        = False
        ),
        title     = 'Tabular Editor Demo',
        id        = 'traitsui.demo.Applications.tabular_editor_demo',
        width     = 0.60,
        height    = 0.75,
        resizable = True
    )

#-- Generate 10,000 random single and married people ---------------------------

male_names = [ 'Michael', 'Edward', 'Timothy', 'James', 'George', 'Ralph',
    'David', 'Martin', 'Bryce', 'Richard', 'Eric', 'Travis', 'Robert', 'Bryan',
    'Alan', 'Harold', 'John', 'Stephen', 'Gael', 'Frederic', 'Eli', 'Scott',
    'Samuel', 'Alexander', 'Tobias', 'Sven', 'Peter', 'Albert', 'Thomas',
    'Horatio', 'Julius', 'Henry', 'Walter', 'Woodrow', 'Dylan', 'Elmer' ]

female_names = [ 'Leah', 'Jaya', 'Katrina', 'Vibha', 'Diane', 'Lisa', 'Jean',
    'Alice', 'Rebecca', 'Delia', 'Christine', 'Marie', 'Dorothy', 'Ellen',
    'Victoria', 'Elizabeth', 'Margaret', 'Joyce', 'Sally', 'Ethel', 'Esther',
    'Suzanne', 'Monica', 'Hortense', 'Samantha', 'Tabitha', 'Judith', 'Ariel',
    'Helen', 'Mary', 'Jane', 'Janet', 'Jennifer', 'Rita', 'Rena', 'Rianna' ]

all_names = male_names + female_names

male_name   = lambda: choice(male_names)
female_name = lambda: choice(female_names)
any_name    = lambda: choice(all_names)
age         = lambda: randint(15, 72)

family_name = lambda: choice([ 'Jones', 'Smith', 'Thompson', 'Hayes', 'Thomas', 'Boyle',
    "O'Reilly", 'Lebowski', 'Lennon', 'Starr', 'McCartney', 'Harrison',
    'Harrelson', 'Steinbeck', 'Rand', 'Hemingway', 'Zhivago', 'Clemens',
    'Heinlien', 'Farmer', 'Niven', 'Van Vogt', 'Sturbridge', 'Washington',
    'Adams', 'Bush', 'Kennedy', 'Ford', 'Lincoln', 'Jackson', 'Johnson',
    'Eisenhower', 'Truman', 'Roosevelt', 'Wilson', 'Coolidge', 'Mack', 'Moon',
    'Monroe', 'Springsteen', 'Rigby', "O'Neil", 'Philips', 'Clinton',
    'Clapton', 'Santana', 'Midler', 'Flack', 'Conner', 'Bond', 'Seinfeld',
    'Costanza', 'Kramer', 'Falk', 'Moore', 'Cramdon', 'Baird', 'Baer',
    'Spears', 'Simmons', 'Roberts', 'Michaels', 'Stuart', 'Montague',
    'Miller' ])

address = lambda: '%d %s %s' % (randint(11, 999), choice([ 'Spring',
    'Summer', 'Moonlight', 'Winding', 'Windy', 'Whispering', 'Falling',
    'Roaring', 'Hummingbird', 'Mockingbird', 'Bluebird', 'Robin', 'Babbling',
    'Cedar', 'Pine', 'Ash', 'Maple', 'Oak', 'Birch', 'Cherry', 'Blossom',
    'Rosewood', 'Apple', 'Peach', 'Blackberry', 'Strawberry', 'Starlight',
    'Wilderness', 'Dappled', 'Beaver', 'Acorn', 'Pecan', 'Pheasant', 'Owl' ]),
    choice([ 'Way', 'Lane', 'Boulevard', 'Street', 'Drive', 'Circle',
    'Avenue', 'Trail' ]))

people = [ Person(name    = '%s %s' % (any_name(), family_name()),
                   age     = age(),
                   address = address()) for i in range(5000) ]

marrieds = [ (MarriedPerson(name    = '%s %s' % (female_name(), last_name),
                              age     = age(),
                              address = address),
               MarriedPerson(name    = '%s %s' % (male_name(), last_name),
                              age     = age(),
                              address = address))
             for last_name, address in
                 [ (family_name(), address()) for i in range(2500) ] ]

for female, male in marrieds:
    female.partner = male
    male.partner   = female
    people.extend([ female, male ])

shuffle(people)

# Create the demo:
demo = Report(people = people)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

