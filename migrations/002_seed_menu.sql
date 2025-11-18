-- ============================
-- PASTRY
-- ============================
INSERT INTO menu_item (title, description, image_url, origin, category, tags, flavor_profiles, dietary_features, price) VALUES
('Black Forest Cake', '黑森林蛋糕 - German chocolate cake with cherries and brandy', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/black_forest.jpg', 'german', 'pastry',
 ARRAY['chocolate','cherry','layered'], ARRAY['sweet','rich'], ARRAY['contains_alcohol','contains_gluten','contains_dairy'], 89.00),

('Macarons', '意式马卡龙 - French almond meringue cookies with various fillings', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/macarons.jpg', 'french', 'pastry',
 ARRAY['macaron','almond','delicate'], ARRAY['sweet','delicate'], ARRAY['contains_nuts','gluten_free','vegetarian'], 69.00),

('Cedric Grolet Pastry', '法式甜品慕斯 - French modernist fruit-inspired pastries', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/cedric_grolet.jpg', 'french', 'pastry',
 ARRAY['mousse','modern','artistic'], ARRAY['sweet','fruity'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 99.00),

('Tiramisu', '提拉米苏 - Italian coffee-flavored dessert with mascarpone', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/tiramisu.jpg', 'italian', 'pastry',
 ARRAY['coffee','mascarpone','ladyfingers'], ARRAY['sweet','bitter','creamy'], ARRAY['contains_alcohol','contains_gluten','contains_dairy'], 59.00),

('Portuguese Egg Tart', '葡式蛋挞 - Creamy custard tarts with caramelized tops', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/egg_tart.jpg', 'macau', 'pastry',
 ARRAY['custard','tart','caramelized'], ARRAY['sweet','creamy','eggy'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 39.00),

('Tiger Skin Swiss Roll', '虎皮蛋糕 - Chinese patterned cake roll with cream filling', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/swiss_roll.jpg', 'chinese', 'pastry',
 ARRAY['swiss_roll','patterned','cream'], ARRAY['sweet','light'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 49.00),

('Baileys Strawberry Cake', '百利甜酒草莓蛋糕 - Cream cake with Baileys and fresh strawberries', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/baileys.jpg', 'fusion', 'pastry',
 ARRAY['strawberry','cream','liqueur'], ARRAY['sweet','creamy','fruity'], ARRAY['contains_alcohol','contains_gluten','contains_dairy','vegetarian'], 59.00),

('Blueberry Chocolate Cake', '蓝莓巧克力蛋糕 - Chocolate cake with blueberry compote', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/blueberry.jpg', 'fusion', 'pastry',
 ARRAY['blueberry','chocolate','layered'], ARRAY['sweet','rich','fruity'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 59.00),

('Mango Mousse Cake', '爱心芒果慕斯蛋糕 - Heart-shaped mango mousse cake', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/mango_mousse.jpg', 'fusion', 'pastry',
 ARRAY['mousse','mango','heart'], ARRAY['sweet','fruity','light'], ARRAY['contains_dairy','gluten_free','vegetarian'], 59.00),

('Strawberry Mousse Cake', '爱心草莓慕斯蛋糕 - Heart-shaped strawberry mousse cake', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/strawberry_mousse.jpg', 'fusion', 'pastry',
 ARRAY['mousse','strawberry','heart'], ARRAY['sweet','fruity','light'], ARRAY['contains_dairy','gluten_free','vegetarian'], 59.00),

('Watermelon Cake', '西瓜蛋糕 - Novelty cake shaped and flavored like watermelon', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/watermelon.jpg', 'fusion', 'pastry',
 ARRAY['watermelon','novelty','summer'], ARRAY['sweet','fruity','refreshing'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 199.00),

('Cream Puffs', '泡芙 - Choux pastry puffs with vanilla, chocolate, or matcha filling', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/cream_puff.jpg', 'french', 'pastry',
 ARRAY['choux','cream','puff'], ARRAY['sweet','creamy','light'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 89.00),

('Ice Cream', '冰淇淋 - Homemade ice cream in vanilla, chocolate, or matcha', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/ice_cream.jpg', 'french', 'pastry',
 ARRAY['ice_cream','frozen','creamy'], ARRAY['sweet','creamy','cold'], ARRAY['contains_dairy','gluten_free','vegetarian'], 89.00),

('Fresh Fruit Cake', '水果蛋糕 - Cake decorated with seasonal fresh fruits', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/fruit_cake.jpg', 'fusion', 'pastry',
 ARRAY['fruit','fresh','seasonal'], ARRAY['sweet','fruity','light'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 89.00),

('Taro Cake', '芋泥蛋糕 - Soft cake with taro paste filling', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/taro_cake.jpg', 'chinese', 'pastry',
 ARRAY['taro','purple','asian'], ARRAY['sweet','earthy','creamy'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 69.00);

-- ============================
-- DESSERT
-- ============================
INSERT INTO menu_item (title, description, image_url, origin, category, tags, flavor_profiles, dietary_features, price) VALUES
('Mango Pancake', '芒果班戟 - Thin crepes filled with fresh mango and cream', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/mango_pancake.jpg', 'hong_kong', 'dessert',
 ARRAY['mango','crepe','cream'], ARRAY['sweet','fruity','creamy'], ARRAY['contains_dairy','gluten_free','vegetarian'], 39.00),

('Tangyuan', '汤圆 - Glutinous rice balls in sweet syrup', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/tang_yuan.jpg', 'chinese', 'dessert',
 ARRAY['rice_ball','sweet','traditional'], ARRAY['sweet','chewy','warm'], ARRAY['gluten_free','vegan'], 39.00),

('Sticky Rice Tamale', '粽子 - Glutinous rice dumplings wrapped in bamboo leaves', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/tamale.jpg', 'chinese', 'dessert',
 ARRAY['sticky_rice','dumpling','traditional'], ARRAY['savory','umami','aromatic'], ARRAY['gluten_free','contains_pork'], 59.00),

('Mooncake', '月饼 - Traditional Chinese pastries for Mid-Autumn Festival', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/mooncake.jpg', 'chinese', 'dessert',
 ARRAY['mooncake','festival','traditional'], ARRAY['sweet','rich','dense'], ARRAY['contains_gluten','vegetarian'], 59.00),

('Animal Cookies', '动物饼干 - Buttery cookies in fun animal shapes', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/cookie.jpg', 'american', 'dessert',
 ARRAY['cookies','butter','animal'], ARRAY['sweet','buttery','crunchy'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 49.00);

-- ============================
-- ENTREE
-- ============================
INSERT INTO menu_item (title, description, image_url, origin, category, tags, flavor_profiles, dietary_features, price) VALUES
('Korean Fried Chicken Wings', '韩式鸡翅 - Crispy fried chicken wings with Korean seasoning', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/chicken_wing.jpg', 'korean', 'entree',
 ARRAY['chicken','fried','spicy'], ARRAY['spicy','savory','crispy'], ARRAY['contains_gluten'], 99.00),

('Steamed Sea Bass', '清蒸鲈鱼 - Fresh sea bass steamed with ginger and scallions', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/steaming_fish.jpg', 'chinese', 'entree',
 ARRAY['fish','steamed','healthy'], ARRAY['savory','umami','light'], ARRAY['gluten_free','contains_shellfish'], 99.00),

('Sour Beef Soup', '酸汤肥牛 - Tangy beef soup with vegetables and spices', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/sour_beef_soup.jpg', 'chinese', 'entree',
 ARRAY['soup','beef','sour'], ARRAY['sour','spicy','savory'], ARRAY['gluten_free'], 49.00),

('Sichuan Spicy Chicken', '辣子鸡 - Crispy chicken with dried chilies and Sichuan peppercorns', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/spicy_chicken.jpg', 'chinese', 'entree',
 ARRAY['chicken','sichuan','spicy'], ARRAY['spicy','numbing','savory'], ARRAY['gluten_free'], 59.00),

('Griddle Cooked Mushrooms', '干锅茶树菇 - Tea tree mushrooms cooked in a dry pot', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/mushrooms.jpg', 'chinese', 'entree',
 ARRAY['mushroom','griddle','vegetarian'], ARRAY['savory','umami','aromatic'], ARRAY['gluten_free','vegan'], 59.00),

('Kung Pao Chicken', '宫保鸡丁 - Stir-fried chicken with peanuts and vegetables', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/kungpao.jpg', 'chinese', 'entree',
 ARRAY['chicken','kungpao','stir_fry'], ARRAY['spicy','savory','nutty'], ARRAY['contains_nuts','gluten_free'], 39.00),

('Grilled Fish', '烤鱼 - Whole fish grilled with spices and herbs', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/grill_fish.jpg', 'chinese', 'entree',
 ARRAY['fish','grilled','whole'], ARRAY['savory','smoky','aromatic'], ARRAY['gluten_free','contains_shellfish'], 99.00),

('Crystal Shrimp Dumplings', '水晶虾饺 - Translucent dumplings filled with fresh shrimp', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/dumpling.jpg', 'chinese', 'entree',
 ARRAY['dumpling','shrimp','steamed'], ARRAY['savory','umami','delicate'], ARRAY['gluten_free','contains_shellfish'], 69.00),

('Vegetable Steamed Buns', '素菜包子 - Soft steamed buns filled with mixed vegetables', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/bum.jpg', 'chinese', 'entree',
 ARRAY['bun','steamed','vegetable'], ARRAY['savory','soft','umami'], ARRAY['vegan','contains_gluten'], 69.00),

('Griddle Pork Intestines', '干锅肥肠 - Pork intestines cooked in a spicy dry pot', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/intestines.jpg', 'chinese', 'entree',
 ARRAY['pork','intestine','griddle'], ARRAY['spicy','savory','chewy'], ARRAY['contains_pork','gluten_free'], 59.00),

('Yuxiang Shredded Pork', '鱼香肉丝 - Shredded pork in fish-fragrant sauce', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/shredded_pork.jpg', 'chinese', 'entree',
 ARRAY['pork','shredded','stir_fry'], ARRAY['sour','spicy','sweet'], ARRAY['contains_pork','gluten_free'], 49.00);

-- ============================
-- RICE & NOODLES
-- ============================
INSERT INTO menu_item (title, description, image_url, origin, category, tags, flavor_profiles, dietary_features, price) VALUES
('Steamed White Rice', '白米饭 - Plain steamed jasmine rice', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/white_rice.jpg', 'chinese', 'rice_and_noodles',
 ARRAY['rice','steamed','plain'], ARRAY['neutral','soft'], ARRAY['vegan','gluten_free'], 2.99),

('Haiga Rice', '胚芽米 - Japanese partially polished rice with germ', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/haiga_rice.jpg', 'japanese', 'rice_and_noodles',
 ARRAY['rice','japanese','haiga'], ARRAY['nutty','chewy'], ARRAY['vegan','gluten_free'], 3.99),

('Chongqing Noodles', '重庆小面 - Spicy Sichuan-style noodles with broth', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/chongqing_noodles.jpg', 'chinese', 'rice_and_noodles',
 ARRAY['noodles','spicy','sichuan'], ARRAY['spicy','numbing','savory'], ARRAY['contains_gluten'], 59.00),

('Beef Noodles', '李先生加州牛肉面 - Beef broth noodles with tender beef slices', 'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/beef_noodles.jpg', 'chinese', 'rice_and_noodles',
 ARRAY['noodles','beef','soup'], ARRAY['savory','rich','umami'], ARRAY['contains_gluten'], 59.00);