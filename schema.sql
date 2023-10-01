-- ###################################################################################################################################### 
-- Coffee Database

DROP TABLE IF EXISTS varieties;

CREATE TABLE varieties
(
    var_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rating DECIMAL,
    num_of_ratings INTEGER,
    description TEXT,
    sweetness DECIMAL,
    body DECIMAL,
    flavor DECIMAL
);

INSERT INTO varieties (name, rating, num_of_ratings, description, sweetness, body, flavor)
VALUES  ('Rubiaceae', NULL, NULL, 'Family of all coffee plants', NULL, NULL, NULL),
        ('Coffea Arabica', NULL, NULL, 'Main species of coffea, generally varieties of arabica are sweet, chocolaty and fruity.', 7, 5, 2),
        ('Coffea Canephora', NULL, NULL, 'Second largest species of coffee after arabica, also called robusta. More resistant but with strong bitterness. Used in blends to increae the body of coffee.', -8, 9, 8),
        ('Gesha', 5, 10, 'Excellent tasting coffee originating from Ethiopia. Exotic with notes of jasmine.', 9, 5, -10),
        ('Typica', 4, 10, 'Major varitey of arabica that is widely spread all over the world. Excellent taste and mouthfeel with fruity notes.', 7, 5, -2),
        ('Bourbon', 4, 10, 'Important variety evolved on the island of Bourbon. Famous for its sweetness and cup quality.', 9, 5, 5),
        ('Timor', 3, 10, 'Crossbreed between arabica and robusta. Higher resistence to disease, but unfortunately lower cup quality.',-4, 8, 6),
        ('Caturra', 3.5, 10, 'Sweetness inhereted from bourbon variety, with floral notes.', 8, 4, -6),
        ('Maragogipe', 4, 10, 'Pleasantyly acidic with distinct characteristics of the region. Popular becuse of it`s large berries.', 0, 4, -8),
        ('Mundo Nuovo', 3.5, 10, 'Crossbreed between Typica and Bourbon. Characteristic sweetness, low acidity and full body.', 9, 8, 2),
        ('Catuai', 3, 10, 'Very productive coffee popular in Brazil. Known for herbal taste with a bitter finnish.', -4, 5, -2),
        ('Catimor', 2.5, 10, 'Coffee resulting from Caturra and Timor variety with full-bodied and spicy notes.', -6, 9, 3),
        ('SL-28', 5, 10, 'The most famous variety from Scott`s Labs (SL prefix). Famous forrest berry flavors with great complexity and acidity.', 4, 5, -8);

DROP TABLE IF EXISTS regions;

CREATE TABLE regions
(
    var_id INTEGER,
    region TEXT NOT NULL
);
INSERT INTO regions (var_id, region)
VALUES  (4, 'Central America'), -- Gesha
        (5, 'Central America'), -- Typica
        (5, 'South America'),
        (5, 'Central Africa'),
        (5, 'East Africa'),
        (5, 'South Eastern Asia'),
        (5, 'South Asia'),
        (6, 'Central America'), -- Bourbon
        (6, 'South America'),
        (7, 'South Eastern Asia'), -- Timor
        (8, 'South America'), -- Caturra
        (12, 'East Africa'), -- Catimor
        (9, 'South America'), -- Maragogipe
        (10, 'South America'), -- Mundo Nuovo
        (11, 'South America'), -- Catuai
        (13, 'East Africa'); -- SL-28


DROP TABLE IF EXISTS genetic_relations;

CREATE TABLE genetic_relations
(
    var_id_ancestor INTEGER,
    var_id_descendant INTEGER
);

INSERT INTO genetic_relations (var_id_ancestor, var_id_descendant)
VALUES  (2,6),
        (2,5),
        (2,7),
        (3,7),
        (2,4),
        (6,8),
        (5,9),
        (5,10),
        (6,10),
        (8,11),
        (10,11),
        (7,12),
        (8,12),
        (6,13);

DROP TABLE IF EXISTS flavors;

CREATE TABLE flavors
(
    var_id INTEGER,
    flavor TEXT NOT NULL
);

INSERT INTO flavors (var_id, flavor)
VALUES  (2, 'Sweet'), -- Arabica
        (2, 'Chocolate'),
        (2, 'Nutty'),
        (2, 'Caramel'),
        (2, 'Fruity'),
        (2, 'Floral'),
        (3, 'Bitter'), -- Robusta
        (4, 'Floral'), -- Gesha
        (4, 'Fruity'), 
        (5, 'Fruity'), -- Typica
        (5, 'Floral'),
        (5, 'Complex'),
        (6, 'Caramel'), -- Bourbon
        (6, 'Sweet'),
        (7, 'Chocolate'), -- Timor
        (7, 'Bitter'), 
        (8, 'Caramel'), -- Caturra
        (8, 'Fruity'),
        (9, 'Acidic'), -- Maragogipe
        (10, 'Sweet'), -- Mundo Nuovo
        (11, 'Fruity'), -- Catuai
        (11, 'Herbal'),
        (11, 'Bitter'),
        (12, 'Spices'), -- Catimor
        (13, 'Fruity'), -- SL-28
        (13, 'Acidic');

-- ###################################################################################################################################### 
-- Users Database

DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY NOT NULL,
    password TEXT NOT NULL,
    mail TEXT NOT NULL,
    user_type TEXT NOT NULL
);

DROP TABLE IF EXISTS user_preferences;

CREATE TABLE user_preferences
(
    user_id TEXT,
    sweetness DECIMAL,
    body DECIMAL,
    flavor DECIMAL
);

DROP TABLE IF EXISTS user_flavors;

CREATE TABLE user_flavors
(
    user_id TEXT,
    flavor TEXT
);