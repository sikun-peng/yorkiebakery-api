-- ============================
-- PASTRY
-- ============================
INSERT INTO menu_item (title, description, image_url, origin, category, tags, flavor_profiles, dietary_features, price) VALUES
('Black Forest Cake', '黑森林蛋糕 - German chocolate cake with cherries and brandy', 'https://d2pdj881wm30p5.cloudfront.net/menu/black_forest.jpg', 'german', 'pastry',
 ARRAY['chocolate','cherry','layered'], ARRAY['sweet','rich'], ARRAY['contains_alcohol','contains_gluten','contains_dairy'], 89.00),

('Macarons', '马卡龙 - French almond meringue cookies with various fillings', 'https://d2pdj881wm30p5.cloudfront.net/menu/macarons.jpg', 'french', 'pastry',
 ARRAY['macaron','almond','delicate'], ARRAY['sweet','delicate'], ARRAY['contains_nuts','gluten_free','vegetarian'], 69.00),

('Cedric Grolet Pastry', '法式甜品慕斯 - French modernist fruit-inspired pastries', 'https://d2pdj881wm30p5.cloudfront.net/menu/cedric_grolet.jpg', 'french', 'pastry',
 ARRAY['mousse','modern','artistic'], ARRAY['sweet','fruity'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 99.00),

('Tiramisu', '提拉米苏 - Italian coffee-flavored dessert with mascarpone', 'https://d2pdj881wm30p5.cloudfront.net/menu/tiramisu.jpg', 'italian', 'pastry',
 ARRAY['coffee','mascarpone','ladyfingers'], ARRAY['sweet','bitter','creamy'], ARRAY['contains_alcohol','contains_gluten','contains_dairy'], 59.00),

('Portuguese Egg Tart', '葡式蛋挞 - Creamy custard tarts with caramelized tops', 'https://d2pdj881wm30p5.cloudfront.net/menu/egg_tart.jpg', 'macau', 'pastry',
 ARRAY['custard','tart','caramelized'], ARRAY['sweet','creamy','eggy'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 39.00),

('Tiger Skin Swiss Roll', '虎皮蛋糕 - Chinese patterned cake roll with cream filling', 'https://d2pdj881wm30p5.cloudfront.net/menu/swiss_roll.jpg', 'chinese', 'pastry',
 ARRAY['swiss_roll','patterned','cream'], ARRAY['sweet','light'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 49.00),

('Baileys Strawberry Cake', '百利甜酒草莓蛋糕 - Cream cake with Baileys and fresh strawberries', 'https://d2pdj881wm30p5.cloudfront.net/menu/baileys.jpg', 'fusion', 'pastry',
 ARRAY['strawberry','cream','liqueur'], ARRAY['sweet','creamy','fruity'], ARRAY['contains_alcohol','contains_gluten','contains_dairy','vegetarian'], 59.00),

('Blueberry Chocolate Cake', '蓝莓巧克力蛋糕 - Chocolate cake with blueberry compote', 'https://d2pdj881wm30p5.cloudfront.net/menu/blueberry.jpg', 'fusion', 'pastry',
 ARRAY['blueberry','chocolate','layered'], ARRAY['sweet','rich','fruity'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 59.00),

('Mango Mousse Cake', '爱心芒果慕斯蛋糕 - Heart-shaped mango mousse cake', 'https://d2pdj881wm30p5.cloudfront.net/menu/mango_mousse.jpg', 'fusion', 'pastry',
 ARRAY['mousse','mango','heart'], ARRAY['sweet','fruity','light'], ARRAY['contains_dairy','gluten_free','vegetarian'], 59.00),

('Strawberry Mousse Cake', '爱心草莓慕斯蛋糕 - Heart-shaped strawberry mousse cake', 'https://d2pdj881wm30p5.cloudfront.net/menu/strawberry_mousse.jpg', 'fusion', 'pastry',
 ARRAY['mousse','strawberry','heart'], ARRAY['sweet','fruity','light'], ARRAY['contains_dairy','gluten_free','vegetarian'], 59.00),

('Watermelon Cake', '西瓜蛋糕 - Novelty cake shaped and flavored like watermelon', 'https://d2pdj881wm30p5.cloudfront.net/menu/watermelon.jpg', 'fusion', 'pastry',
 ARRAY['watermelon','novelty','summer'], ARRAY['sweet','fruity','refreshing'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 199.00),

('Cream Puffs', '泡芙 - Choux pastry puffs with vanilla, chocolate, or matcha filling', 'https://d2pdj881wm30p5.cloudfront.net/menu/cream_puff.jpg', 'french', 'pastry',
 ARRAY['choux','cream','puff'], ARRAY['sweet','creamy','light'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 89.00),

('Ice Cream', '冰淇淋 - Homemade ice cream in vanilla, chocolate, or matcha', 'https://d2pdj881wm30p5.cloudfront.net/menu/ice_cream.jpg', 'french', 'pastry',
 ARRAY['ice_cream','frozen','creamy'], ARRAY['sweet','creamy','cold'], ARRAY['contains_dairy','gluten_free','vegetarian'], 89.00),

('Fresh Fruit Cake', '水果蛋糕 - Cake decorated with seasonal fresh fruits', 'https://d2pdj881wm30p5.cloudfront.net/menu/fruit_cake.jpg', 'fusion', 'pastry',
 ARRAY['fruit','fresh','seasonal'], ARRAY['sweet','fruity','light'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 89.00),

('Taro Cake', '芋泥蛋糕 - Soft cake with taro paste filling', 'https://d2pdj881wm30p5.cloudfront.net/menu/taro_cake.jpg', 'chinese', 'pastry',
 ARRAY['taro','purple','asian'], ARRAY['sweet','earthy','creamy'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 69.00);

-- ============================
-- DESSERT
-- ============================
INSERT INTO menu_item (title, description, image_url, origin, category, tags, flavor_profiles, dietary_features, price) VALUES
('Mango Pancake', '芒果班戟 - Thin crepes filled with fresh mango and cream', 'https://d2pdj881wm30p5.cloudfront.net/menu/mango_pancake.jpg', 'hong_kong', 'dessert',
 ARRAY['mango','crepe','cream'], ARRAY['sweet','fruity','creamy'], ARRAY['contains_dairy','gluten_free','vegetarian'], 39.00),

('Tangyuan', '汤圆 - Glutinous rice balls in sweet syrup', 'https://d2pdj881wm30p5.cloudfront.net/menu/tang_yuan.jpg', 'chinese', 'dessert',
 ARRAY['rice_ball','sweet','traditional'], ARRAY['sweet','chewy','warm'], ARRAY['gluten_free','vegan'], 39.00),

('Sticky Rice Tamale', '粽子 - Glutinous rice dumplings wrapped in bamboo leaves', 'https://d2pdj881wm30p5.cloudfront.net/menu/tamale.jpg', 'chinese', 'dessert',
 ARRAY['sticky_rice','dumpling','traditional'], ARRAY['savory','umami','aromatic'], ARRAY['gluten_free','contains_pork'], 59.00),

('Mooncake', '月饼 - Traditional Chinese pastries for Mid-Autumn Festival', 'https://d2pdj881wm30p5.cloudfront.net/menu/mooncake.jpg', 'chinese', 'dessert',
 ARRAY['mooncake','festival','traditional'], ARRAY['sweet','rich','dense'], ARRAY['contains_gluten','vegetarian'], 59.00),

('Animal Cookies', '动物饼干 - Buttery cookies in fun animal shapes', 'https://d2pdj881wm30p5.cloudfront.net/menu/cookie.jpg', 'american', 'dessert',
 ARRAY['cookies','butter','animal'], ARRAY['sweet','buttery','crunchy'], ARRAY['contains_gluten','contains_dairy','vegetarian'], 49.00);

-- ============================
-- ENTREE
-- ============================
INSERT INTO menu_item (title, description, image_url, origin, category, tags, flavor_profiles, dietary_features, price) VALUES
('Korean Fried Chicken Wings', '韩式鸡翅 - Crispy fried chicken wings with Korean seasoning', 'https://d2pdj881wm30p5.cloudfront.net/menu/chicken_wing.jpg', 'korean', 'entree',
 ARRAY['chicken','fried','spicy'], ARRAY['spicy','savory','crispy'], ARRAY['spicy'], 99.00),

('Steamed Sea Bass', '清蒸鲈鱼 - Fresh sea bass steamed with ginger and scallions', 'https://d2pdj881wm30p5.cloudfront.net/menu/steaming_fish.jpg', 'chinese', 'entree',
 ARRAY['fish','steamed','healthy'], ARRAY['savory','umami','light'], ARRAY['gluten_free','contains_shellfish'], 99.00),

('Sour Beef Soup', '酸汤肥牛 - Tangy beef soup with vegetables and spices', 'https://d2pdj881wm30p5.cloudfront.net/menu/sour_beef_soup.jpg', 'chinese', 'entree',
 ARRAY['soup','beef','sour'], ARRAY['sour','spicy','savory'], ARRAY['gluten_free'], 49.00),

('Sichuan Spicy Chicken', '辣子鸡 - Crispy chicken with dried chilies and Sichuan peppercorns', 'https://d2pdj881wm30p5.cloudfront.net/menu/spicy_chicken.jpg', 'chinese', 'entree',
 ARRAY['chicken','sichuan','spicy'], ARRAY['spicy','numbing','savory'], ARRAY['spicy'], 59.00),

('Griddle Cooked Mushrooms', '干锅茶树菇 - Tea tree mushrooms cooked in a dry pot', 'https://d2pdj881wm30p5.cloudfront.net/menu/mushrooms.jpg', 'chinese', 'entree',
 ARRAY['mushroom','griddle','vegetarian'], ARRAY['savory','umami','aromatic'], ARRAY['gluten_free','vegan'], 59.00),

('Kung Pao Chicken', '宫保鸡丁 - Stir-fried chicken with peanuts and vegetables', 'https://d2pdj881wm30p5.cloudfront.net/menu/kungpao.jpg', 'chinese', 'entree',
 ARRAY['chicken','kungpao','stir_fry'], ARRAY['spicy','savory','nutty'], ARRAY['contains_nuts','gluten_free'], 39.00),

('Grilled Fish', '烤鱼 - Whole fish grilled with spices and herbs', 'https://d2pdj881wm30p5.cloudfront.net/menu/grill_fish.jpg', 'chinese', 'entree',
 ARRAY['fish','grilled','whole'], ARRAY['savory','smoky','aromatic'], ARRAY['gluten_free','contains_shellfish'], 99.00),

('Crystal Shrimp Dumplings', '水晶虾饺 - Translucent dumplings filled with fresh shrimp', 'https://d2pdj881wm30p5.cloudfront.net/menu/dumpling.jpg', 'chinese', 'entree',
 ARRAY['dumpling','shrimp','steamed'], ARRAY['savory','umami','delicate'], ARRAY['gluten_free','contains_shellfish'], 69.00),

('Vegetable Steamed Buns', '素菜包子 - Soft steamed buns filled with mixed vegetables', 'https://d2pdj881wm30p5.cloudfront.net/menu/bum.jpg', 'chinese', 'entree',
 ARRAY['bun','steamed','vegetable'], ARRAY['savory','soft','umami'], ARRAY['vegan','contains_gluten'], 69.00),

('Griddle Pork Intestines', '干锅肥肠 - Pork intestines cooked in a spicy dry pot', 'https://d2pdj881wm30p5.cloudfront.net/menu/intestines.jpg', 'chinese', 'entree',
 ARRAY['pork','intestine','griddle'], ARRAY['spicy','savory','chewy'], ARRAY['contains_pork','spicy'], 59.00),

('Yangcheng Lake Hairy Crab', '阳澄湖大闸蟹 - Steamed premium hairy crab known for its sweet, delicate meat and rich golden roe', 'https://d2pdj881wm30p5.cloudfront.net/menu/hairy_crab.jpg', 'chinese', 'entree',
 ARRAY['crab','steamed','premium'], ARRAY['sweet','delicate','rich'], ARRAY['gluten_free','contains_shellfish'], 99.00),

('Yuxiang Shredded Pork', '鱼香肉丝 - Shredded pork in fish-fragrant sauce', 'https://d2pdj881wm30p5.cloudfront.net/menu/shredded_pork.jpg', 'chinese', 'entree',
 ARRAY['pork','shredded','stir_fry'], ARRAY['sour','spicy','sweet'], ARRAY['contains_pork','gluten_free'], 49.00);

-- ============================
-- RICE & NOODLES
-- ============================
INSERT INTO menu_item (title, description, image_url, origin, category, tags, flavor_profiles, dietary_features, price) VALUES
('Steamed White Rice', '白米饭 - Plain steamed jasmine rice', 'https://d2pdj881wm30p5.cloudfront.net/menu/white_rice.jpg', 'chinese', 'rice_and_noodles',
 ARRAY['rice','steamed','plain'], ARRAY['neutral','soft'], ARRAY['vegan','gluten_free'], 2.99),

('Haiga Rice', '胚芽米 - Japanese partially polished rice with germ', 'https://d2pdj881wm30p5.cloudfront.net/menu/haiga_rice.jpg', 'japanese', 'rice_and_noodles',
 ARRAY['rice','japanese','haiga'], ARRAY['nutty','chewy'], ARRAY['vegan','gluten_free'], 3.99),

('Chongqing Noodles', '重庆小面 - Spicy Sichuan-style noodles with broth', 'https://d2pdj881wm30p5.cloudfront.net/menu/chongqing_noodles.jpg', 'chinese', 'rice_and_noodles',
 ARRAY['noodles','spicy','sichuan'], ARRAY['spicy','numbing','savory'], ARRAY['contains_gluten', 'spicy'], 59.00),

('Beef Noodles', '李先生加州牛肉面 - Beef broth noodles with tender beef slices', 'https://d2pdj881wm30p5.cloudfront.net/menu/beef_noodles.jpg', 'chinese', 'rice_and_noodles',
 ARRAY['noodles','beef','soup'], ARRAY['savory','rich','umami'], ARRAY['contains_gluten'], 59.00);


-- ============================
-- DRINKS
-- ============================
INSERT INTO menu_item (title, description, image_url, origin, category, tags, flavor_profiles, dietary_features, price) VALUES
('Boba Milk Tea', '珍珠奶茶 - Sweet tea with tapioca pearls and milk', 'https://d2pdj881wm30p5.cloudfront.net/menu/boba_milk_tea.jpg', 'taiwanese', 'drink',
 ARRAY['bubble_tea','tapioca','milky'], ARRAY['sweet','creamy','chewy'], ARRAY['contains_dairy','vegetarian'], 6.99),

('American Black Coffee', '美式黑咖啡 - Classic brewed black coffee', 'https://d2pdj881wm30p5.cloudfront.net/menu/black_coffee.jpg', 'american', 'drink',
 ARRAY['coffee','black','brewed'], ARRAY['bitter','bold','aromatic'], ARRAY['vegan','gluten_free'], 3.99),

('Espresso', '意式浓缩咖啡 - Strong concentrated coffee shot', 'https://d2pdj881wm30p5.cloudfront.net/menu/espresso.jpg', 'italian', 'drink',
 ARRAY['espresso','strong','concentrated'], ARRAY['bitter','intense','rich'], ARRAY['vegan','gluten_free'], 4.49),

('Latte', '拿铁咖啡 - Espresso with steamed milk', 'https://d2pdj881wm30p5.cloudfront.net/menu/latte.jpg', 'italian', 'drink',
 ARRAY['latte','milky','espresso'], ARRAY['creamy','smooth','balanced'], ARRAY['contains_dairy','vegetarian'], 5.99),

('Cappuccino', '卡布奇诺 - Espresso with equal parts steamed milk and foam', 'https://d2pdj881wm30p5.cloudfront.net/menu/cappuccino.jpg', 'italian', 'drink',
 ARRAY['cappuccino','foamy','espresso'], ARRAY['creamy','light','balanced'], ARRAY['contains_dairy','vegetarian'], 5.99),

('Matcha Latte', '抹茶拿铁 - Green tea powder with steamed milk', 'https://d2pdj881wm30p5.cloudfront.net/menu/matcha_latte.jpg', 'japanese', 'drink',
 ARRAY['matcha','green_tea','milky'], ARRAY['earthy','creamy','sweet'], ARRAY['contains_dairy','vegetarian'], 6.49),


('Thai Iced Tea', '泰式冰奶茶 - Sweet spiced tea with condensed milk', 'https://d2pdj881wm30p5.cloudfront.net/menu/thai_tea.jpg', 'thai', 'drink',
 ARRAY['thai_tea','orange','sweet'], ARRAY['sweet','creamy','spiced'], ARRAY['contains_dairy','vegetarian'], 6.99),

('Lemonade', '新鲜柠檬水 - Freshly squeezed lemon with sugar', 'https://d2pdj881wm30p5.cloudfront.net/menu/lemonade.jpg', 'american', 'drink',
 ARRAY['lemonade','refreshing','citrus'], ARRAY['sour','sweet','refreshing'], ARRAY['vegan','gluten_free'], 4.99),

('Iced Americano', '冰美式咖啡 - Espresso shots over ice and water', 'https://d2pdj881wm30p5.cloudfront.net/menu/americano_iced.jpg', 'american', 'drink',
 ARRAY['iced_coffee','cold','refreshing'], ARRAY['bold','smooth','refreshing'], ARRAY['vegan','gluten_free'], 4.49),

('Mocha', '摩卡咖啡 - Espresso with chocolate and steamed milk', 'https://d2pdj881wm30p5.cloudfront.net/menu/mocha.jpg', 'italian', 'drink',
 ARRAY['mocha','chocolate','coffee'], ARRAY['sweet','chocolatey','creamy'], ARRAY['contains_dairy','vegetarian'], 6.49),

('Green Tea', '绿茶 - Traditional Japanese green tea', 'https://d2pdj881wm30p5.cloudfront.net/menu/green_tea.jpg', 'japanese', 'drink',
 ARRAY['green_tea','traditional','healthy'], ARRAY['earthy','grassy','light'], ARRAY['vegan','gluten_free'], 3.49),

('Orange Juice', '鲜榨橙汁 - Freshly squeezed orange juice', 'https://d2pdj881wm30p5.cloudfront.net/menu/orange_juice.jpg', 'american', 'drink',
 ARRAY['orange_juice','fresh','vitamin_c'], ARRAY['sweet','tangy','refreshing'], ARRAY['vegan','gluten_free'], 4.99),

('Soda', '汽水 - Various carbonated soft drinks', '', 'american', 'drink',
 ARRAY['soda','carbonated','refreshing'], ARRAY['sweet','fizzy','cold'], ARRAY['vegan','gluten_free'], 2.99);