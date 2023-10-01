from database import get_db, close_db


class variety_class:
    def __init__(self, var_id, name, rating, num_of_ratings, description, sweetness, body, flavor, regions=[], flavors=[], parents=[]):
        self.var_id = var_id
        self.name = name
        self.rating = rating
        self.num_of_ratings = num_of_ratings
        self.description = description
        self.sweetness = sweetness
        self.body = body
        self.flavor = flavor
        self.regions = regions
        self.flavors = flavors
        self.parents = parents

    def attributes(self):
        return vars(self)

    def get_regions(self):
        db = get_db()
        regions_dicts = db.execute("""SELECT region FROM  regions
        WHERE var_id = ?;""", (self.var_id,)).fetchall()
        close_db()
        regions = [region['region'] for region in regions_dicts]
        self.regions = regions
        return regions

    def get_flavors(self):
        db = get_db()
        flavors_dicts = db.execute("""SELECT flavor FROM flavors
        WHERE var_id = ?;""", (self.var_id,)).fetchall()
        close_db()
        flavors = [flavor['flavor'] for flavor in flavors_dicts]
        self.flavors = flavors
        return flavors

    def get_parents(self, var_id=None):
        parents = []
        db = get_db()
        if var_id:
            parents_sql = db.execute(
                """SELECT var_id_ancestor AS parent_id FROM genetic_relations WHERE var_id_descendant = ?;""", (var_id,)).fetchall()
        else:
            parents_sql = db.execute(
                """SELECT var_id_ancestor AS parent_id FROM genetic_relations WHERE var_id_descendant = ?;""", (self.var_id,)).fetchall()
        close_db()
        for parent_sql in parents_sql:
            parents.append(parent_sql['parent_id'])
        if var_id is None:
            self.parents = parents
        return parents

    def get_children(self, var_id=None):
        children = []
        db = get_db()
        if var_id:
            children_sql = db.execute(
                """SELECT var_id_descendant AS child_id FROM genetic_relations WHERE var_id_ancestor = ?;""", (var_id,)).fetchall()
        else:
            children_sql = db.execute(
                """SELECT var_id_descendant AS child_id FROM genetic_relations WHERE var_id_ancestor = ?;""", (self.var_id,)).fetchall()
        close_db()
        for child_sql in children_sql:
            children.append(child_sql['child_id'])
        if var_id is None:
            self.children = children
        return children

    def update_variety(self):
        db = get_db()
        db.execute("""UPDATE varieties
        SET var_id = ?, name=?, rating=?, num_of_ratings=?, description=?, sweetness=?, body=?, flavor=?
        WHERE var_id=?;
        """, (self.var_id, self.name, self.rating, self.num_of_ratings, self.description, self.sweetness, self.body, self.flavor, self.var_id))
        db.commit()
        close_db()

    def update_regions(self):
        db = get_db()
        db.execute("""DELETE FROM regions WHERE var_id = ?;""", (self.var_id,))
        db.commit()
        close_db()
        self.add_regions()

    def update_flavors(self):
        db = get_db()
        db.execute("""DELETE FROM flavors WHERE var_id=?;""", (self.var_id,))
        db.commit()
        close_db()
        self.add_flavors()

    def delete_variety(self):
        db = get_db()
        db.execute("""DELETE FROM varieties WHERE var_id=?;""", (self.var_id,))
        db.execute("""DELETE FROM regions WHERE var_id=?;""", (self.var_id,))
        db.execute("""DELETE FROM flavors WHERE var_id=?;""", (self.var_id,))
        db.execute(
            """DELETE FROM genetic_relations WHERE var_id_descendant=?;""", (self.var_id,))
        db.commit()
        close_db()

    def add_variety(self):
        db = get_db()
        db.execute("""INSERT INTO varieties (  name, rating,  num_of_ratings, description, sweetness, body, flavor)
        VALUES ( ?, ?, ?, ?, ?, ?, ?);""", (self.name, self.rating, self.num_of_ratings, self.description, self.sweetness, self.body, self.flavor))
        db.commit()
        var_id = db.execute("""SELECT var_id FROM varieties 
        WHERE name = ? AND description = ?;""", (self.name, self.description)).fetchone()
        self.var_id = var_id['var_id']
        close_db()

    def add_regions(self):
        db = get_db()
        regions = self.regions
        var_id = self.var_id
        for region in regions:
            db.execute("""INSERT INTO regions 
            VALUES (?, ?);""", (var_id, region))
            db.commit()
        close_db()

    def add_flavors(self):
        db = get_db()
        flavors = self.flavors
        var_id = self.var_id
        for flavor in flavors:
            db.execute("""INSERT INTO flavors 
            VALUES (?, ?);""", (var_id, flavor))
            db.commit()
        close_db()

    def add_relations(self):
        db = get_db()
        parents = self.parents
        var_id = self.var_id
        for parent in parents:
            db.execute("""INSERT INTO genetic_relations
            VALUES (?,?);""", (parent, var_id))
            db.commit()
        close_db()

    def get_ancestors_id(self, var_id):
        # recursive function
        # base case is that it reached var_id 1
        # call the recursive function on all parents
        if var_id == 2 or var_id == 3:
            return [var_id]
        else:
            parents = self.get_parents(var_id)
            ancestor_list = []
            for parent_id in parents:
                returned_ancestor_list = self.get_ancestors_id(parent_id)
                for ancestor_id in returned_ancestor_list:
                    if ancestor_id not in ancestor_list:
                        ancestor_list.append(ancestor_id)
                if var_id not in ancestor_list:
                    ancestor_list.append(var_id)
            return ancestor_list

    def get_descendants_id(self, var_id):
        # Recursive function
        # base case is that it reached a leaf
        # call the recursive function on its parents
        children = self.get_children(var_id)
        if children == []:
            return [var_id]
        else:
            descendants_list = []
            for child_id in children:
                returned_descendants_list = self.get_descendants_id(child_id)
                for descendant_id in returned_descendants_list:
                    if descendant_id not in descendants_list:
                        descendants_list.append(descendant_id)
                if var_id not in descendants_list:
                    descendants_list.append(var_id)
            return descendants_list

########################################################################################################################


class user:
    def __init__(self, user_id, password, mail, type, sweetness=None, body=None, flavor=None, flavors=None):
        self.user_id = user_id
        self.password = password
        self.mail = mail
        self.type = type
        self.sweetness = sweetness
        self.body = body
        self.flavor = flavor
        self.flavors = flavors

    def attributes(self):
        return vars(self)

    def update_user(self, changed_user_id=None):
        # Cannot update the user id, because it breaks
        if changed_user_id==None:
            changed_user_id = self.user_id
        db = get_db()
        db.execute("""UPDATE users
        SET user_id = ?, password=?, mail=?, user_type=?
        WHERE user_id=?;
        """, (changed_user_id, self.password, self.mail, self.type, self.user_id))
        db.commit()
        if self.sweetness and self.body and self.flavor:
            db.execute("""UPDATE user_preferences
        SET user_id = ?, sweetness=?, body=?, flavor=?
        WHERE user_id=?;
        """, (changed_user_id, self.sweetness, self.body, self.flavor, self.user_id))
            db.commit()
        self.user_id = changed_user_id
        if self.flavors:
            self.delete_user_flavors()
            self.add_user_flavors()

        close_db()



    def get_user_preferences(self):
        db = get_db()
        preferences_sql = db.execute("""SELECT * FROM user_preferences WHERE user_id = ?;""", (self.user_id,)).fetchone()
        self.sweetness = preferences_sql['sweetness']
        self.body = preferences_sql['body']
        self.flavor = preferences_sql['flavor']
        close_db()
    
    def get_flavors(self):
        db = get_db()
        flavors_sql = db.execute("""SELECT flavor FROM user_flavors WHERE user_id = ?;""", (self.user_id,)).fetchall()
        close_db()
        flavors = [flavor_sql['flavor'] for flavor_sql in flavors_sql]
        self.flavors = flavors
        return flavors

    def delete_user(self):
        db = get_db()
        db.execute("""DELETE FROM users
        WHERE user_id=?;""", (self.user_id,))
        db.commit()
        close_db()

    def add_user(self):
        db = get_db()
        db.execute("""INSERT INTO users (user_id, password, mail, user_type)
        VALUES (?, ?, ?, ?);""", (self.user_id, self.password, self.mail, self.type))
        db.commit()
        close_db()

    def add_user_flavors(self):
        db = get_db()
        for flavor in self.flavors:
            db.execute("""INSERT INTO user_flavors(user_id, flavor)
            VALUES (?, ?);""", (self.user_id, flavor))
            db.commit()
        close_db()

    def add_user_preferences(self):
        db = get_db()
        db.execute("""INSERT INTO user_preferences (user_id, sweetness, body, flavor)
        VALUES (?, ?, ?, ?);""", (self.user_id, self.sweetness, self.body, self.flavor))
        db.commit()
        close_db()

    def delete_user_flavors(self):
        db = get_db()
        db.execute("""DELETE FROM user_flavors
        WHERE user_id = ?;""", (self.user_id,))
        db.commit()
        close_db()

    def get_flavor_coords(self):
        # The individual flavors the user chose will be turned into a number m, which the distance will be multiplied with. M will be closer to 0.5 if many flavors match up and 1.5 if none match the chosen ones. m will be based on the number of chosen flavors 'c' and how many matched up 's', it should give 1.5 if none match up and  0.5 if a all of them do. So m = 1.5 - s/p
        db = get_db()
        varieties = db.execute(
            """SELECT var_id, sweetness, body, flavor FROM varieties WHERE sweetness IS NOT NULL AND body IS NOT NULL AND flavor IS NOT NULL AND var_id > 3;""").fetchall()
        flavor_coords_dict = {}
        user_flavors = self.flavors
        c = len(user_flavors)
        for variety in varieties:
            if c == 0:
                m = 1
            else:
                var_flavors_sql = db.execute(
                    """SELECT flavor FROM flavors WHERE var_id=?;""", (variety['var_id'],)).fetchall()
                var_flavors = [var_flavor['flavor']
                               for var_flavor in var_flavors_sql]
                s = 0
                for var_flavor in var_flavors:
                    if var_flavor in user_flavors:
                        s += 1
                c = len(user_flavors)
                m = 1.5 - s/c
            flavor_coords_dict[variety['var_id']] = (float(variety['sweetness']), float(
                variety['body']), float(variety['flavor']), m)
        close_db()
        return flavor_coords_dict

    def get_preferences(self):
        # Idea is to represent the coffee varieties as a 3D metric space where the distance between two point (x,y,z) and (a,b,c) is set by the formula ((x-a)^2+(y-b)^2+(z-c)^2)
        # The users preferences will be treated as sort of a perfect variety and represented in the 3D metric space as well, the axes being sweetness, body, flavor. Then we will find the distances between them.
        flavor_coords = self.get_flavor_coords()
        user_coord = (float(self.sweetness), float(
            self.body), float(self.flavor))
        flavor_distances_dict = {}
        for var_id in flavor_coords.keys():
            distance = ((flavor_coords[var_id][0]-user_coord[0])**2 + (
                flavor_coords[var_id][1]-user_coord[1])**2+(flavor_coords[var_id][2]-user_coord[2])**2)
            m = flavor_coords[var_id][3]
            measure = distance*m
            flavor_distances_dict[var_id] = measure
        # Rank the measures
        # Code taken from https://realpython.com/sort-python-dictionary/
        ranked_measures = dict(
            sorted(flavor_distances_dict.items(), key=lambda item: item[1]))
        return ranked_measures
    
    def test_done_check(self):
        db = get_db()
        previous_entry = db.execute("""SELECT * FROM user_preferences WHERE user_id = ?;""", (self.user_id,)). fetchall()
        close_db()
        test_done = True
        if previous_entry == []:
            test_done = False
        return test_done

    
