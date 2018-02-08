"""
A non-class-specific way to update postgresql's autoincrementing primary key
sequences, useful for running after data including primary key values has been
seeded.

Similar to set_val_user_id() from Ratings, but works on all classes in
model.py.

Author: Katie Byers

"""

from sqlalchemy import func
from sqlalchemy.inspection import inspect
from model import db


def update_pkey_seqs():
    """Set primary key for each table to start at one higher than the current
    highest key. Helps when data has been manually seeded."""

    # get a dictionary of {classname: class} for all classes in model.py
    model_classes = db.Model._decl_class_registry

    # loop over the classes
    for class_name in model_classes:

        # the dictionary will include a helper class we don't care about, so
        # skip it
        if class_name == "_sa_module_registry":
            continue

        # print("-" * 40)
        # print("Working on class", class_name)

        # get the class itself out of the dictionary
        cls = model_classes[class_name]

        # get the name of the table associated with the class and its primary
        # key
        table_name = cls.__tablename__
        pkey_column = inspect(cls).primary_key[0]
        primary_key = pkey_column.name
        # print("Table name:", table_name, "Primary key:", primary_key)

        # check to see if the primary key is an integer (which are
        # autoincrementing by default)
        # if it isn't, skip to the next class
        if (not isinstance(pkey_column.type, db.Integer) or
            pkey_column.autoincrement is not True):
            # print("Not an autoincrementing integer key - skipping.")
            continue

        # now we know we're dealing with an autoincrementing key, so get the
        # highest id value currently in the table
        result = db.session.query(func.max(getattr(cls, primary_key))).first()

        # if the table is empty, result will be none; only proceed if it's not
        # (we have to index at 0 since the result comes back as a tuple)
        if result[0]:
            # cast the result to an int
            max_id = int(result[0])
            # print("highest id:", max_id)

            # set the next value to be max + 1
            query = ("SELECT setval('" + table_name + "_" + primary_key +
                     "_seq', :new_id)")
            db.session.execute(query, {'new_id': max_id + 1})
            db.session.commit()
            # print("Primary key sequence updated.")
        # else:
            # print("No records found. No update made.")

    # we're done!
    # print("-" * 40)
    
