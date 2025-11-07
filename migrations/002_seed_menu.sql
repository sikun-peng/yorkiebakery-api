-- FRENCH / JAPANESE PASTRIES & DESSERTS
INSERT INTO menu_item (title, description, image_url, cuisine, dish_type, tags, flavor_profile, dietary_restrictions, price)
VALUES
('Butter Croissant', 'Flaky laminated dough with a tender crumb.', NULL, 'french','pastry', ARRAY['classic','buttery'], ARRAY['buttery','flaky','light'], ARRAY['vegetarian'], 4.50),
('Almond Croissant', 'Frangipane-filled croissant with toasted almonds.', NULL, 'french','pastry', ARRAY['almond','sweet'], ARRAY['buttery','nutty','sweet'], ARRAY['vegetarian','contains_nuts'], 5.50),
('Pistachio-Raspberry Croissant', 'Pistachio cream with raspberry jam.', NULL, 'french','pastry', ARRAY['seasonal','pistachio'], ARRAY['sweet','tart','nutty'], ARRAY['vegetarian','contains_nuts'], 5.95),
('Pain au Chocolat', 'Two batons of dark chocolate in flaky pastry.', NULL, 'french','pastry', ARRAY['chocolate'], ARRAY['buttery','chocolatey','rich'], ARRAY['vegetarian'], 4.95),
('Vanilla Mille-Feuille', 'Crisp puff pastry layers with vanilla diplomat cream.', NULL, 'french','dessert', ARRAY['classic'], ARRAY['creamy','light','sweet'], ARRAY['vegetarian'], 6.95),
('Lemon Tartlet', 'Buttery shell with bright lemon curd.', NULL, 'french','dessert', ARRAY['tart','citrus'], ARRAY['tart','buttery','sweet'], ARRAY['vegetarian'], 6.50),
('Chocolate Tartlet', 'Silky dark chocolate ganache in sable crust.', NULL, 'french','dessert', ARRAY['chocolate','rich'], ARRAY['rich','chocolatey','smooth'], ARRAY['vegetarian'], 6.75),
('Raspberry Macaron', 'Crisp shell with raspberry buttercream.', NULL, 'french','dessert', ARRAY['macaron','raspberry'], ARRAY['sweet','tart','airy'], ARRAY['vegetarian','contains_nuts'], 2.50),
('Pistachio Macaron', 'Nutty pistachio cream filling.', NULL, 'french','dessert', ARRAY['macaron','pistachio'], ARRAY['sweet','nutty','airy'], ARRAY['vegetarian','contains_nuts'], 2.50),
('Crème Brûlée', 'Vanilla custard with caramelized sugar crust.', NULL, 'french','dessert', ARRAY['custard'], ARRAY['creamy','rich','caramel'], ARRAY['vegetarian'], 7.95),
('Matcha Roll Cake', 'Airy sponge with matcha cream swirl.', NULL, 'japanese','dessert', ARRAY['matcha','sponge'], ARRAY['light','herbal','sweet'], ARRAY['vegetarian'], 6.25),
('Strawberry Shortcake (Jap.)', 'Soft sponge, fresh cream, strawberries.', NULL, 'japanese','dessert', ARRAY['shortcake','seasonal'], ARRAY['light','creamy','fruity'], ARRAY['vegetarian'], 6.95),
('Yuzu Cheesecake', 'Citrus-forward baked cheesecake with yuzu zest.', NULL, 'japanese','dessert', ARRAY['yuzu','citrus'], ARRAY['tart','creamy','light'], ARRAY['vegetarian'], 7.50),
('Black Sesame Cream Puff', 'Choux filled with black sesame cream.', NULL, 'japanese','dessert', ARRAY['sesame','choux'], ARRAY['nutty','creamy','light'], ARRAY['vegetarian','contains_nuts'], 5.50),
('Hokkaido Milk Bread Slice', 'Pillowy-soft slightly sweet bread.', NULL, 'japanese','bread', ARRAY['milk_bread'], ARRAY['soft','light','slightly_sweet'], ARRAY['vegetarian'], 3.25),
('Opera Cake Slice', 'Layers of almond joconde, coffee buttercream, ganache.', NULL, 'french','dessert', ARRAY['opera','coffee'], ARRAY['rich','coffee','chocolatey'], ARRAY['vegetarian','contains_nuts'], 7.95),
('Paris-Brest', 'Choux ring with praline cream.', NULL, 'french','dessert', ARRAY['praline'], ARRAY['nutty','creamy','sweet'], ARRAY['vegetarian','contains_nuts'], 7.25),
('Canelé', 'Caramelized crust, custardy interior with vanilla-rum notes.', NULL, 'french','dessert', ARRAY['canele'], ARRAY['caramel','vanilla','chewy'], ARRAY['vegetarian'], 3.95);

-- DRINKS (CAFÉ / THAI / KOREAN INFLUENCE)
INSERT INTO menu_item (title, description, image_url, cuisine, dish_type, tags, flavor_profile, dietary_restrictions, price) VALUES
('Café au Lait', 'House brew with steamed milk.', NULL, 'french','drink', ARRAY['coffee'], ARRAY['smooth','creamy'], ARRAY['vegetarian'], 4.25),
('Espresso', 'Double shot, balanced and bright.', NULL, 'french','drink', ARRAY['coffee'], ARRAY['bold','roasty'], ARRAY[]::text[], 3.50),
('Matcha Latte', 'Ceremonial-grade matcha, micro-foamed milk.', NULL, 'japanese','drink', ARRAY['matcha'], ARRAY['herbal','creamy','light_sweet'], ARRAY['vegetarian'], 5.25),
('Hojicha Latte', 'Roasted green tea latte, nutty and mellow.', NULL, 'japanese','drink', ARRAY['hojicha'], ARRAY['nutty','toasty','light'], ARRAY['vegetarian'], 5.25),
('Thai Iced Tea', 'Brewed Thai tea with milk over ice.', NULL, 'thai','drink', ARRAY['iced','sweet'], ARRAY['creamy','sweet','spiced'], ARRAY['vegetarian'], 4.95),
('Lychee Iced Tea', 'Black tea with lychee syrup and fruit.', NULL, 'thai','drink', ARRAY['fruit_tea'], ARRAY['floral','fruity','refreshing'], ARRAY['vegetarian'], 4.75),
('Korean Yuzu Honey Tea', 'Citrus marmalade infusion (hot).', NULL, 'korean','drink', ARRAY['yuzu','citrus'], ARRAY['tart','sweet','soothing'], ARRAY['vegetarian'], 4.50),
('Cold Brew', '12-hour steep, chocolatey finish.', NULL, 'american','drink', ARRAY['coffee','cold_brew'], ARRAY['smooth','chocolatey'], ARRAY[]::text[], 4.50);

-- CHINESE ENTREES / APPETIZERS (Style M: authentic, moderate spice)
INSERT INTO menu_item (title, description, image_url, cuisine, dish_type, tags, flavor_profile, dietary_restrictions, price) VALUES
('Mapo Tofu (Pork)', 'Sichuan peppercorn, doubanjiang, silky tofu.', NULL, 'chinese','entree', ARRAY['sichuan','tofu'], ARRAY['spicy','numbing','umami'], ARRAY[]::text[], 18.50),
('Mapo Tofu (Vegetarian)', 'Mushroom mince, peppercorn, doubanjiang.', NULL, 'chinese','entree', ARRAY['sichuan','tofu','veg'], ARRAY['spicy','numbing','umami'], ARRAY['vegetarian'], 17.50),
('Three-Cup Chicken', 'Soy, rice wine, basil, ginger; glossy reduction.', NULL, 'chinese','entree', ARRAY['taiwanese','basil'], ARRAY['umami','herbal','savory'], ARRAY[]::text[], 20.00),
('Cantonese Roast Pork (Char Siu) Plate', 'Honey glaze, jasmine rice, greens.', NULL, 'chinese','entree', ARRAY['bbq','char_siu'], ARRAY['sweet_savory','umami'], ARRAY[]::text[], 21.00),
('Beef Chow Fun', 'Wok-hei wide rice noodles, bean sprouts, scallion.', NULL, 'chinese','entree', ARRAY['wok','noodles'], ARRAY['smoky','umami','savory'], ARRAY[]::text[], 19.50),
('Dan Dan Noodles', 'Sesame-spicy sauce, pork mince, greens, peanuts.', NULL, 'chinese','entree', ARRAY['sichuan','noodles'], ARRAY['spicy','nutty','umami'], ARRAY['contains_nuts'], 18.00),
('Garlic Green Beans', 'Wok-tossed with ginger-garlic and soy.', NULL, 'chinese','side', ARRAY['veggie'], ARRAY['garlic','savory','crisp'], ARRAY['vegan'], 10.50),
('Scallion Pancake', 'Crisp layers with scallion aroma.', NULL, 'chinese','appetizer', ARRAY['flatbread'], ARRAY['savory','flaky'], ARRAY['vegan'], 9.50),
('Salt & Pepper Shrimp', 'Lightly battered shrimp with chili-salt.', NULL, 'chinese','appetizer', ARRAY['seafood'], ARRAY['peppery','savory','crisp'], ARRAY[]::text[], 14.50),
('Hot & Sour Soup', 'Mushroom, tofu, bamboo, egg ribbons.', NULL, 'chinese','appetizer', ARRAY['soup'], ARRAY['tangy','peppery','umami'], ARRAY[]::text[], 8.50),
('Curry Chicken Rice (HK-Style)', 'Mild yellow curry, potato, carrot, rice.', NULL, 'chinese','entree', ARRAY['hk_cafe'], ARRAY['mild_spice','comforting','savory'], ARRAY[]::text[], 18.50),
('Tomato & Egg Over Rice', 'Soft-scrambled egg with tomato sauce.', NULL, 'chinese','entree', ARRAY['home_style'], ARRAY['tangy','umami','comforting'], ARRAY['vegetarian'], 15.50),
('Fried Rice (Yangzhou)', 'Char siu, shrimp, egg, peas, wok aroma.', NULL, 'chinese','entree', ARRAY['fried_rice'], ARRAY['umami','smoky','satisfying'], ARRAY[]::text[], 17.50),
('Sichuan Cucumber Salad', 'Chili oil, garlic, vinegar, sesame.', NULL, 'chinese','appetizer', ARRAY['cold_dish'], ARRAY['spicy','tangy','refreshing'], ARRAY['vegan','contains_nuts'], 7.95);

-- THAI ENTREES / APPETIZERS (Style M: authentic, medium spice)
INSERT INTO menu_item (title, description, image_url, cuisine, dish_type, tags, flavor_profile, dietary_restrictions, price) VALUES
('Pad Thai (Shrimp)', 'Tamarind sauce, egg, tofu bits, chive, peanut, lime.', NULL, 'thai','entree', ARRAY['noodles'], ARRAY['sweet_savory','tangy','peanut'], ARRAY['contains_nuts'], 19.50),
('Pad Thai (Tofu)', 'Vegetarian pad thai with balanced tamarind.', NULL, 'thai','entree', ARRAY['noodles','veg'], ARRAY['sweet_savory','tangy'], ARRAY['vegetarian','contains_nuts'], 18.00),
('Pad See Ew (Beef)', 'Wide rice noodles with soy, gai lan, egg.', NULL, 'thai','entree', ARRAY['noodles'], ARRAY['umami','smoky','slightly_sweet'], ARRAY[]::text[], 19.50),
('Green Curry (Chicken)', 'Coconut milk, Thai basil, eggplant, bamboo.', NULL, 'thai','entree', ARRAY['curry'], ARRAY['spicy','herbal','creamy'], ARRAY[]::text[], 21.00),
('Red Curry (Tofu)', 'Coconut base with fragrant red curry paste.', NULL, 'thai','entree', ARRAY['curry','veg'], ARRAY['spicy','creamy','aromatic'], ARRAY['vegetarian'], 19.50),
('Thai Basil Beef', 'Wok-fried beef, chili, garlic, holy basil, rice.', NULL, 'thai','entree', ARRAY['stir_fry'], ARRAY['spicy','herbal','umami'], ARRAY[]::text[], 20.50),
('Tom Yum Soup', 'Spicy-sour broth, lemongrass, galangal, mushroom.', NULL, 'thai','appetizer', ARRAY['soup'], ARRAY['tangy','spicy','aromatic'], ARRAY[]::text[], 9.50),
('Som Tum (Papaya Salad)', 'Shredded green papaya with chili-lime dressing.', NULL, 'thai','appetizer', ARRAY['salad'], ARRAY['crisp','tart','spicy'], ARRAY['contains_nuts'], 10.50),
('Thai Fried Chicken', 'Crispy, marinated with herbs and fish sauce.', NULL, 'thai','appetizer', ARRAY['fried'], ARRAY['savory','crisp','umami'], ARRAY[]::text[], 12.50),
('Pineapple Fried Rice', 'Turmeric rice, egg, shrimp, cashews.', NULL, 'thai','entree', ARRAY['fried_rice','fruity'], ARRAY['sweet_savory','aromatic'], ARRAY['contains_nuts'], 18.50),
('Pad Kra Pao (Pork)', 'Chili-garlic ground pork, basil, fried egg.', NULL, 'thai','entree', ARRAY['spicy_basil'], ARRAY['spicy','herbal','umami'], ARRAY[]::text[], 20.00),
('Mango Sticky Rice (Seasonal)', 'Sweet mango, coconut sticky rice, sesame.', NULL, 'thai','dessert', ARRAY['seasonal'], ARRAY['fruity','sweet','coconut'], ARRAY['vegetarian'], 8.95);

-- KOREAN & WESTERN BISTRO
INSERT INTO menu_item (title, description, image_url, cuisine, dish_type, tags, flavor_profile, dietary_restrictions, price) VALUES
('Bulgogi Beef Bowl', 'Soy-sesame marinated beef over rice, pickles.', NULL, 'korean','entree', ARRAY['rice_bowl'], ARRAY['sweet_savory','umami','sesame'], ARRAY[]::text[], 19.50),
('Kimchi Fried Rice', 'Fried rice with kimchi, scallion, fried egg.', NULL, 'korean','entree', ARRAY['fried_rice'], ARRAY['spicy','tangy','umami'], ARRAY[]::text[], 17.50),
('Tteokbokki', 'Spicy rice cakes, fish cake, gochujang sauce.', NULL, 'korean','appetizer', ARRAY['street_food'], ARRAY['spicy','chewy','sweet_savory'], ARRAY[]::text[], 13.50),
('Korean Fried Chicken (Soy Garlic)', 'Crispy double-fried wings.', NULL, 'korean','appetizer', ARRAY['fried','wings'], ARRAY['garlic','savory','crisp'], ARRAY[]::text[], 14.50),
('Bibimbap (Veg)', 'Mixed rice bowl, assorted veggies, gochujang.', NULL, 'korean','entree', ARRAY['mixed_bowl','veg'], ARRAY['spicy','umami','fresh'], ARRAY['vegetarian'], 18.50),
('Steak Frites (8oz)', 'Seared bavette, herb butter, pommes frites.', NULL, 'american','entree', ARRAY['bistro','steak'], ARRAY['savory','buttery','rich'], ARRAY[]::text[], 28.00),
('Grilled Salmon Plate', 'Lemon butter, seasonal veg, herbed rice.', NULL, 'american','entree', ARRAY['seafood'], ARRAY['bright','buttery','savory'], ARRAY[]::text[], 26.00),
('Mushroom Cream Pasta', 'Cremini and shiitake in light cream sauce.', NULL, 'american','entree', ARRAY['pasta','veg'], ARRAY['creamy','umami','herbal'], ARRAY['vegetarian'], 19.50),
('Chicken Pesto Panini', 'Basil pesto, mozzarella, tomato, press-grilled.', NULL, 'american','entree', ARRAY['sandwich'], ARRAY['herbal','savory','cheesy'], ARRAY[]::text[], 15.50),
('Tomato Basil Soup', 'Roasted tomato, basil, olive oil finish.', NULL, 'american','appetizer', ARRAY['soup'], ARRAY['tangy','herbal','comfort'], ARRAY['vegetarian'], 7.95),
('Caesar Salad', 'Romaine, parmigiano, croutons, house dressing.', NULL, 'american','appetizer', ARRAY['salad'], ARRAY['umami','creamy','peppery'], ARRAY[]::text[], 10.50),
('Truffle Fries', 'Hand-cut fries, truffle oil, parmesan.', NULL, 'american','side', ARRAY['fries'], ARRAY['savory','aromatic','crisp'], ARRAY[]::text[], 8.95);

-- A FEW FUSION / SEASONAL SPECIALS
INSERT INTO menu_item (title, description, image_url, cuisine, dish_type, tags, flavor_profile, dietary_restrictions, price) VALUES
('Yuzu Basque Cheesecake Slice', 'Lightly burnt top, citrus finish.', NULL, 'fusion','dessert', ARRAY['yuzu','cheesecake'], ARRAY['creamy','tart','light'], ARRAY['vegetarian'], 7.95),
('Pistachio-Rose Éclair', 'Pistachio cream with rose glaze.', NULL, 'fusion','dessert', ARRAY['eclair','pistachio','rose'], ARRAY['floral','nutty','sweet'], ARRAY['vegetarian','contains_nuts'], 6.95),
('Thai Basil Chicken Croissant Sandwich', 'Savory basil chicken in buttery croissant.', NULL, 'fusion','entree', ARRAY['croissant_sandwich'], ARRAY['herbal','savory','umami'], ARRAY[]::text[], 15.95),
('Kimchi Tuna Melt', 'Spicy kimchi, cheddar, albacore, pressed.', NULL, 'fusion','entree', ARRAY['sandwich'], ARRAY['spicy','savory','tangy'], ARRAY[]::text[], 14.95),
('Black Pepper Beef Baguette', 'Peppery beef, pickled veg, baguette.', NULL, 'fusion','entree', ARRAY['baguette'], ARRAY['peppery','umami','crisp'], ARRAY[]::text[], 15.95);