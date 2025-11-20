INSERT INTO menu_item (
    title, description, image_url, origin, category,
    tags, flavor_profiles, dietary_features, price, is_available
) VALUES
('Matcha Roll Cake', 'Soft matcha sponge rolled with light cream.', '', 'japanese', 'dessert',
 ARRAY['matcha','roll_cake'], ARRAY['earthy','light','sweet'], ARRAY['contains_dairy'], 5.99, FALSE),

('Taro Mochi Donut', 'Chewy donut made with taro glaze.', '', 'taiwanese', 'dessert',
 ARRAY['taro','mochi'], ARRAY['chewy','sweet'], ARRAY['gluten_free'], 4.99, FALSE),

('Mini Éclair', 'Small choux filled with vanilla cream.', '', 'french', 'dessert',
 ARRAY['eclair','vanilla'], ARRAY['light','sweet'], ARRAY['contains_dairy'], 4.29, FALSE),

('Sweet Potato Bread', 'Korean-style sweet potato–shaped bun.', '', 'korean', 'pastry',
 ARRAY['sweet_potato'], ARRAY['earthy','sweet'], ARRAY['vegetarian'], 3.99, FALSE),

('Thai Coconut Cookie', 'Crispy coconut cookie with toasted edges.', '', 'thai', 'dessert',
 ARRAY['coconut','cookie'], ARRAY['sweet','toasty'], ARRAY['gluten_free'], 3.39, FALSE),

('Chocolate Biscotti Mini', 'Crunchy chocolate biscotti.', '', 'italian', 'dessert',
 ARRAY['biscotti','chocolate'], ARRAY['crunchy','sweet'], ARRAY['contains_gluten'], 3.29, FALSE),

('Ube Butter Cookie', 'Chewy purple yam cookie.', '', 'fusion', 'dessert',
 ARRAY['ube','cookie'], ARRAY['chewy','sweet'], ARRAY['gluten_free'], 3.99, FALSE),

('Black Sesame Latte Cake', 'Nutty black sesame layered sponge.', '', 'korean', 'dessert',
 ARRAY['black_sesame'], ARRAY['nutty','creamy'], ARRAY['contains_dairy'], 5.29, FALSE),

('Apple Tartlet', 'Caramelized apples on buttery tart crust.', '', 'french', 'dessert',
 ARRAY['apple','tart'], ARRAY['fruity','sweet'], ARRAY['contains_gluten'], 5.59, FALSE),

('Brown Sugar Castella', 'Fluffy Taiwanese sponge with brown sugar.', '', 'taiwanese', 'dessert',
 ARRAY['castella','brown_sugar'], ARRAY['airy','sweet'], ARRAY['contains_gluten'], 4.79, FALSE),

('Mochi Brownie Bite', 'Dense chocolate brownie with mochi center.', '', 'fusion', 'dessert',
 ARRAY['brownie','mochi'], ARRAY['chewy','rich'], ARRAY['contains_gluten'], 4.39, FALSE),

('Lemon Olive Oil Cake', 'Bright, fragrant lemon cake.', '', 'italian', 'dessert',
 ARRAY['lemon','cake'], ARRAY['tangy','moist'], ARRAY['vegetarian'], 4.79, FALSE),

('Yuzu Cheesecake Mini', 'Tangy yuzu-flavored mini cheesecake.', '', 'japanese', 'dessert',
 ARRAY['yuzu','cheesecake'], ARRAY['tangy','creamy'], ARRAY['contains_dairy'], 5.49, FALSE),

('Cinnamon Sugar Donut Hole', 'Mini donut holes dusted in cinnamon.', '', 'american', 'dessert',
 ARRAY['donut','cinnamon'], ARRAY['sweet','spiced'], ARRAY['contains_gluten'], 2.99, FALSE),

('Pandan Milk Bun', 'Soft milk bread with pandan flavor.', '', 'thai', 'bread',
 ARRAY['pandan','milk_bread'], ARRAY['fragrant','sweet'], ARRAY['contains_dairy'], 3.79, FALSE),

('Chocolate Mochi Donut', 'Chewy donut with cocoa glaze.', '', 'fusion', 'dessert',
 ARRAY['mochi','chocolate'], ARRAY['chewy','sweet'], ARRAY['contains_gluten'], 4.69, FALSE),

('Mini Tiramisu Cup', 'Creamy tiramisu layered with espresso.', '', 'italian', 'dessert',
 ARRAY['tiramisu','espresso'], ARRAY['creamy','rich'], ARRAY['contains_dairy'], 5.79, FALSE),

('Black Sesame Shortbread', 'Crumbly cookie with sesame aroma.', '', 'taiwanese', 'dessert',
 ARRAY['black_sesame','shortbread'], ARRAY['nutty','crumbly'], ARRAY['vegetarian'], 3.69, FALSE),

('Strawberry Daifuku', 'Mochi filled with strawberry and red bean.', '', 'japanese', 'dessert',
 ARRAY['mochi','strawberry'], ARRAY['fruity','chewy'], ARRAY['gluten_free'], 4.59, FALSE),

('Honey Oolong Cookie', 'Cookie infused with oolong tea.', '', 'taiwanese', 'dessert',
 ARRAY['oolong','cookie'], ARRAY['aromatic','sweet'], ARRAY['contains_gluten'], 3.59, FALSE),

('Garlic Cream Bread', 'Korean garlic cream cheese bread.', '', 'korean', 'pastry',
 ARRAY['garlic','cream'], ARRAY['savory','creamy'], ARRAY['contains_dairy'], 4.99, FALSE),

('Pumpkin Spice Bread', 'Warm pumpkin loaf with spices.', '', 'american', 'dessert',
 ARRAY['pumpkin','spice'], ARRAY['warm','sweet'], ARRAY['contains_gluten'], 4.19, FALSE),

('Hojicha Roll Cake', 'Roasted tea sponge with cream.', '', 'japanese', 'dessert',
 ARRAY['hojicha','roll_cake'], ARRAY['earthy','light'], ARRAY['contains_dairy'], 5.29, FALSE),

('Blueberry Milk Bun', 'Milk bread filled with blueberry jam.', '', 'korean', 'bread',
 ARRAY['blueberry','milk_bread'], ARRAY['fruity','sweet'], ARRAY['contains_dairy'], 3.89, FALSE),

('Carrot Cake Mini', 'Mini carrot cake with cream cheese.', '', 'american', 'dessert',
 ARRAY['carrot','cream_cheese'], ARRAY['sweet','spiced'], ARRAY['contains_dairy'], 4.99, FALSE),

-- ============================
-- ITEMS 26–50
-- ============================

('Matcha Chocolate Chip Cookie', 'Matcha cookie mixed with chocolate chips.', '', 'fusion', 'dessert',
 ARRAY['matcha','cookie'], ARRAY['earthy','sweet'], ARRAY['contains_gluten'], 3.89, FALSE),

('Vanilla Castella Mini', 'Fluffy sponge with light vanilla flavor.', '', 'japanese', 'dessert',
 ARRAY['castella','vanilla'], ARRAY['airy','sweet'], ARRAY['contains_gluten'], 4.39, FALSE),

('Ube Mochi Cake', 'Chewy mochi cake with ube flavor.', '', 'fusion', 'dessert',
 ARRAY['ube','mochi'], ARRAY['chewy','sweet'], ARRAY['gluten_free'], 4.89, FALSE),

('Black Sesame Cream Puff', 'Cream puff filled with sesame cream.', '', 'korean', 'dessert',
 ARRAY['cream_puff','black_sesame'], ARRAY['nutty','creamy'], ARRAY['contains_dairy'], 5.19, FALSE),

('Thai Tea Pound Cake', 'Pound cake infused with Thai tea.', '', 'thai', 'dessert',
 ARRAY['thai_tea','cake'], ARRAY['aromatic','sweet'], ARRAY['contains_dairy'], 4.69, FALSE),

('Oreo Cheesecake Bite', 'Rich cheesecake topped with Oreo crumbs.', '', 'american', 'dessert',
 ARRAY['oreo','cheesecake'], ARRAY['creamy','sweet'], ARRAY['contains_dairy'], 4.49, FALSE),

('Mini Apple Cinnamon Pie', 'Mini pie filled with apple cinnamon mix.', '', 'american', 'dessert',
 ARRAY['apple','cinnamon'], ARRAY['fruity','spiced'], ARRAY['contains_gluten'], 4.39, FALSE),

('Chocolate Lava Mini', 'Small molten chocolate cake.', '', 'american', 'dessert',
 ARRAY['chocolate','lava_cake'], ARRAY['rich','gooey'], ARRAY['contains_gluten'], 5.29, FALSE),

('French Butter Cookie Mini', 'Classic shortbread-style cookie.', '', 'french', 'dessert',
 ARRAY['butter','shortbread'], ARRAY['buttery','light'], ARRAY['contains_gluten'], 2.79, FALSE),

('Mango Sticky Rice Cake', 'Cake version of mango sticky rice.', '', 'thai', 'dessert',
 ARRAY['mango','sticky_rice'], ARRAY['fruity','sweet'], ARRAY['gluten_free'], 5.49, FALSE),

('Red Bean Mochi Donut', 'Mochi donut with red bean glaze.', '', 'fusion', 'dessert',
 ARRAY['mochi','red_bean'], ARRAY['chewy','sweet'], ARRAY['contains_gluten'], 4.79, FALSE),

('Honey Butter Bread Bite', 'Mini honey-soaked crispy toast.', '', 'korean', 'dessert',
 ARRAY['honey','toast'], ARRAY['sweet','buttery'], ARRAY['contains_dairy'], 3.29, FALSE),

('Chocolate Madeleine Mini', 'Chocolate version of classic French madeleine.', '', 'french', 'dessert',
 ARRAY['madeleine','chocolate'], ARRAY['soft','sweet'], ARRAY['contains_gluten'], 3.69, FALSE),

('Coffee Milk Roll', 'Soft bread filled with coffee cream.', '', 'korean', 'bread',
 ARRAY['coffee','cream'], ARRAY['aromatic','creamy'], ARRAY['contains_dairy'], 4.49, FALSE),

('Blueberry Cream Cheese Bun', 'Bun filled with blueberry cream cheese.', '', 'korean', 'pastry',
 ARRAY['blueberry','cream_cheese'], ARRAY['sweet','tangy'], ARRAY['contains_dairy'], 4.69, FALSE),

('Strawberry Cream Roll', 'Japanese-style strawberry cream roll.', '', 'japanese', 'dessert',
 ARRAY['strawberry','cream'], ARRAY['fruity','light'], ARRAY['contains_dairy'], 5.39, FALSE),

('Hazelnut Mini Croissant', 'Small croissant filled with hazelnut cream.', '', 'french', 'pastry',
 ARRAY['hazelnut','croissant'], ARRAY['nutty','buttery'], ARRAY['contains_nuts'], 5.29, FALSE),

('Green Tea Cookie', 'Crunchy cookie flavored with green tea.', '', 'japanese', 'dessert',
 ARRAY['green_tea','cookie'], ARRAY['earthy','crisp'], ARRAY['contains_gluten'], 3.19, FALSE),

('Pineapple Jam Bun', 'Soft bun with pineapple jam.', '', 'taiwanese', 'bread',
 ARRAY['pineapple','jam'], ARRAY['fruity','sweet'], ARRAY['contains_gluten'], 3.69, FALSE),

('Vanilla Cream Donut Hole', 'Mini donut hole with vanilla cream.', '', 'american', 'dessert',
 ARRAY['donut','vanilla'], ARRAY['sweet','creamy'], ARRAY['contains_gluten'], 3.09, FALSE),

('Thai Pandan Cookie', 'Crisp cookie with pandan aroma.', '', 'thai', 'dessert',
 ARRAY['pandan','cookie'], ARRAY['fragrant','sweet'], ARRAY['contains_gluten'], 3.29, FALSE),

('Salted Caramel Tart Mini', 'Small tart filled with salted caramel.', '', 'french', 'dessert',
 ARRAY['caramel','tart'], ARRAY['sweet','salty'], ARRAY['contains_dairy'], 5.19, FALSE),

('Milk Tea Mochi Cake', 'Soft cake flavored like milk tea.', '', 'taiwanese', 'dessert',
 ARRAY['milk_tea','mochi'], ARRAY['chewy','sweet'], ARRAY['contains_gluten'], 4.99, FALSE),

('Miso Butter Cookie', 'Sweet–savory cookie with miso butter.', '', 'fusion', 'dessert',
 ARRAY['miso','butter'], ARRAY['savory','sweet'], ARRAY['contains_gluten'], 3.49, FALSE),

('Caramel Coffee Bun', 'Coffee bun with caramel center.', '', 'fusion', 'bread',
 ARRAY['coffee','caramel'], ARRAY['aromatic','sweet'], ARRAY['contains_dairy'], 4.69, FALSE),

-- ============================
-- ITEMS 51–75
-- ============================

('Banana Mochi Bite', 'Soft banana-flavored mochi bite.', '', 'fusion', 'dessert',
 ARRAY['banana','mochi'], ARRAY['chewy','sweet'], ARRAY['gluten_free'], 3.89, FALSE),

('Matcha Soufflé Bite', 'Mini fluffy matcha soufflé.', '', 'japanese', 'dessert',
 ARRAY['matcha','souffle'], ARRAY['light','airy'], ARRAY['contains_dairy'], 5.19, FALSE),

('Chocolate Cream Pan', 'Soft bun filled with chocolate cream.', '', 'japanese', 'pastry',
 ARRAY['cream','chocolate'], ARRAY['creamy','sweet'], ARRAY['contains_gluten'], 3.99, FALSE),

('Strawberry Yogurt Mousse', 'Light yogurt mousse with strawberry swirl.', '', 'fusion', 'dessert',
 ARRAY['strawberry','mousse'], ARRAY['fruity','creamy'], ARRAY['contains_dairy'], 5.49, FALSE),

('Black Sesame Financier', 'Small almond cake with sesame.', '', 'french', 'dessert',
 ARRAY['sesame','financier'], ARRAY['nutty','buttery'], ARRAY['contains_nuts'], 4.39, FALSE),

('Choco Puff Rice Bar', 'Crunchy puffed rice chocolate bar.', '', 'american', 'dessert',
 ARRAY['chocolate','puff_rice'], ARRAY['crunchy','sweet'], ARRAY['contains_gluten'], 2.79, FALSE),

('Tiramisu Mochi', 'Mochi with creamy tiramisu filling.', '', 'italian', 'dessert',
 ARRAY['mochi','tiramisu'], ARRAY['creamy','chewy'], ARRAY['contains_dairy'], 4.99, FALSE),

('Thai Lime Cookie', 'Bright lime-flavored shortbread.', '', 'thai', 'dessert',
 ARRAY['lime','cookie'], ARRAY['zesty','sweet'], ARRAY['contains_gluten'], 3.29, FALSE),

('Brown Sugar Mochi Bread', 'Chewy bread with brown sugar mochi center.', '', 'taiwanese', 'bread',
 ARRAY['brown_sugar','mochi'], ARRAY['chewy','sweet'], ARRAY['contains_gluten'], 4.39, FALSE),

('Chocolate Castella Square', 'Moist chocolate castella cake.', '', 'japanese', 'dessert',
 ARRAY['castella','chocolate'], ARRAY['soft','rich'], ARRAY['contains_gluten'], 4.79, FALSE),

('Green Tea Swiss Roll', 'Light green tea sponge with cream.', '', 'japanese', 'dessert',
 ARRAY['green_tea','cream'], ARRAY['light','earthy'], ARRAY['contains_dairy'], 5.29, FALSE),

('Maple Butter Cookie', 'Shortbread cookie with maple aroma.', '', 'american', 'dessert',
 ARRAY['maple','cookie'], ARRAY['buttery','sweet'], ARRAY['contains_gluten'], 3.19, FALSE),

('Ricotta Lemon Bar', 'Tangy lemon bar with ricotta layer.', '', 'italian', 'dessert',
 ARRAY['lemon','ricotta'], ARRAY['tangy','smooth'], ARRAY['contains_dairy'], 4.79, FALSE),

('Coffee Jelly Cup', 'Iced coffee jelly with cream.', '', 'japanese', 'dessert',
 ARRAY['coffee','jelly'], ARRAY['bitter','creamy'], ARRAY['contains_dairy'], 4.19, FALSE),

('Hazelnut Chocolate Mini Muffin', 'Mini muffin with hazelnut cream.', '', 'fusion', 'dessert',
 ARRAY['hazelnut','muffin'], ARRAY['nutty','sweet'], ARRAY['contains_nuts'], 3.99, FALSE),

('Pandan Cheese Tart', 'Tart with pandan custard and cheese.', '', 'thai', 'dessert',
 ARRAY['pandan','tart'], ARRAY['fragrant','creamy'], ARRAY['contains_dairy'], 5.39, FALSE),

('Brown Butter Mochi Cake', 'Nutty brown butter mochi cake.', '', 'fusion', 'dessert',
 ARRAY['mochi','brown_butter'], ARRAY['chewy','nutty'], ARRAY['gluten_free'], 4.89, FALSE),

('Strawberry Pudding Cup', 'Soft pudding with strawberry topping.', '', 'american', 'dessert',
 ARRAY['strawberry','pudding'], ARRAY['creamy','sweet'], ARRAY['contains_dairy'], 4.29, FALSE),

('Cocoa Meringue Cookie', 'Light, crispy cocoa meringue.', '', 'french', 'dessert',
 ARRAY['meringue','cocoa'], ARRAY['airy','sweet'], ARRAY['gluten_free'], 3.49, FALSE),

('Black Tea Chiffon Slice', 'Soft chiffon cake flavored with tea.', '', 'japanese', 'dessert',
 ARRAY['black_tea','chiffon'], ARRAY['light','aromatic'], ARRAY['contains_gluten'], 5.29, FALSE),

('Taiwanese Honey Castella', 'Honey-sweet sponge cake.', '', 'taiwanese', 'dessert',
 ARRAY['castella','honey'], ARRAY['airy','sweet'], ARRAY['contains_gluten'], 4.39, FALSE),

('Salted Yolk Puff Mini', 'Flaky pastry with sweet-salty yolk.', '', 'chinese', 'dessert',
 ARRAY['salted_yolk','pastry'], ARRAY['savory','sweet'], ARRAY['contains_gluten'], 4.69, FALSE),

('Milk Tea Pudding Cup', 'Classic milk tea pudding with cream.', '', 'taiwanese', 'dessert',
 ARRAY['milk_tea','pudding'], ARRAY['creamy','sweet'], ARRAY['contains_dairy'], 4.29, FALSE),

('Chocolate Hazelnut Donut Hole', 'Mini donut with chocolate hazelnut glaze.', '', 'fusion', 'dessert',
 ARRAY['donut','hazelnut','chocolate'], ARRAY['rich','sweet'], ARRAY['contains_nuts'], 3.79, FALSE),

('Matcha Mochi Cookie', 'Soft cookie with gooey mochi inside.', '', 'japanese', 'dessert',
 ARRAY['matcha','mochi'], ARRAY['chewy','earthy'], ARRAY['contains_gluten'], 4.19, FALSE),

-- ============================
-- ITEMS 76–100
-- ============================

('Mocha Cream Mini Cup', 'Small cup of mocha-flavored cream dessert.', '', 'american', 'dessert',
 ARRAY['mocha','cream'], ARRAY['creamy','chocolatey'], ARRAY['contains_dairy'], 4.59, FALSE),

('Pandan Mochi Donut Hole', 'Mochi donut hole with pandan icing.', '', 'thai', 'dessert',
 ARRAY['pandan','mochi'], ARRAY['chewy','fragrant'], ARRAY['contains_gluten'], 3.89, FALSE),

('Vanilla Custard Bun', 'Soft bun filled with smooth vanilla custard.', '', 'japanese', 'pastry',
 ARRAY['custard','vanilla'], ARRAY['creamy','sweet'], ARRAY['contains_dairy'], 3.99, FALSE),

('Chocolate Cookie Sandwich', 'Chocolate cookie with cream filling.', '', 'american', 'dessert',
 ARRAY['chocolate','cookie'], ARRAY['sweet','rich'], ARRAY['contains_gluten'], 3.49, FALSE),

('Mango Cream Tart', 'Mini tart topped with mango cream.', '', 'fusion', 'dessert',
 ARRAY['mango','tart'], ARRAY['fruity','creamy'], ARRAY['contains_dairy'], 5.19, FALSE),

('Sweet Corn Mochi Cake', 'Chewy mochi cake with sweet corn flavor.', '', 'taiwanese', 'dessert',
 ARRAY['corn','mochi'], ARRAY['chewy','sweet'], ARRAY['gluten_free'], 4.69, FALSE),

('Thai Coffee Cookie', 'Crispy cookie with Thai-style coffee aroma.', '', 'thai', 'dessert',
 ARRAY['coffee','cookie'], ARRAY['aromatic','sweet'], ARRAY['contains_gluten'], 3.29, FALSE),

('Chocolate Taro Swirl Cake', 'Soft cake with taro and chocolate swirls.', '', 'fusion', 'dessert',
 ARRAY['taro','chocolate'], ARRAY['sweet','soft'], ARRAY['contains_gluten'], 4.79, FALSE),

('Vanilla Mochi Donut', 'Chewy donut with vanilla glaze.', '', 'fusion', 'dessert',
 ARRAY['mochi','vanilla'], ARRAY['chewy','sweet'], ARRAY['contains_gluten'], 4.59, FALSE),

('Mini Almond Cake', 'Small almond flour cake.', '', 'french', 'dessert',
 ARRAY['almond','cake'], ARRAY['nutty','sweet'], ARRAY['contains_nuts'], 4.29, FALSE),

('Coconut Milk Bread', 'Soft bread flavored with coconut milk.', '', 'thai', 'bread',
 ARRAY['coconut','milk_bread'], ARRAY['fragrant','soft'], ARRAY['contains_dairy'], 3.79, FALSE),

('Caramel Mochi Square', 'Chewy mochi square with caramel.', '', 'fusion', 'dessert',
 ARRAY['caramel','mochi'], ARRAY['sweet','chewy'], ARRAY['gluten_free'], 4.29, FALSE),

('Green Tea Pudding Cup', 'Smooth pudding flavored with green tea.', '', 'japanese', 'dessert',
 ARRAY['green_tea','pudding'], ARRAY['light','creamy'], ARRAY['contains_dairy'], 4.29, FALSE),

('Ube Milk Bun', 'Milk bread with ube filling.', '', 'korean', 'bread',
 ARRAY['ube','milk_bread'], ARRAY['soft','sweet'], ARRAY['contains_dairy'], 3.89, FALSE),

('Chocolate Chip Scone Mini', 'Mini scone with chocolate chips.', '', 'american', 'pastry',
 ARRAY['scone','chocolate'], ARRAY['crumbly','sweet'], ARRAY['contains_gluten'], 3.59, FALSE),

('Salted Caramel Mochi Donut', 'Mochi donut with salted caramel glaze.', '', 'fusion', 'dessert',
 ARRAY['caramel','mochi'], ARRAY['chewy','sweet','salty'], ARRAY['contains_gluten'], 4.99, FALSE),

('Miso Chocolate Tart', 'Small chocolate tart with a hint of miso.', '', 'fusion', 'dessert',
 ARRAY['chocolate','miso'], ARRAY['rich','savory'], ARRAY['contains_gluten'], 5.49, FALSE),

('Honey Milk Castella', 'Fluffy castella cake with honey and milk.', '', 'taiwanese', 'dessert',
 ARRAY['castella','milk'], ARRAY['airy','sweet'], ARRAY['contains_dairy'], 4.69, FALSE),

('Matcha Cream Dorayaki', 'Mini dorayaki with matcha cream filling.', '', 'japanese', 'dessert',
 ARRAY['dorayaki','matcha'], ARRAY['sweet','earthy'], ARRAY['contains_gluten'], 4.79, FALSE),

('Strawberry Mochi Cupcake', 'Cupcake with mochi center and strawberry cream.', '', 'fusion', 'dessert',
 ARRAY['strawberry','mochi'], ARRAY['fruity','chewy'], ARRAY['contains_gluten'], 4.89, FALSE),

('Choco Almond Mini Bar', 'Chocolate snack bar with almond crunch.', '', 'american', 'dessert',
 ARRAY['chocolate','almond'], ARRAY['nutty','sweet'], ARRAY['contains_nuts'], 3.49, FALSE),

('Pandan Kaya Bun', 'Soft bun filled with pandan kaya jam.', '', 'thai', 'pastry',
 ARRAY['pandan','kaya'], ARRAY['creamy','sweet'], ARRAY['contains_dairy'], 3.99, FALSE),

('Black Sesame Butter Mochi', 'Nutty butter mochi with sesame.', '', 'japanese', 'dessert',
 ARRAY['black_sesame','mochi'], ARRAY['nutty','chewy'], ARRAY['gluten_free'], 4.79, FALSE),

('Sweet Red Bean Tart', 'Mini tart with sweet red bean filling.', '', 'japanese', 'dessert',
 ARRAY['red_bean','tart'], ARRAY['sweet','smooth'], ARRAY['contains_gluten'], 4.69, FALSE),

('Mini Coconut Cheesecake', 'Cheesecake with coconut cream.', '', 'fusion', 'dessert',
 ARRAY['coconut','cheesecake'], ARRAY['creamy','sweet'], ARRAY['contains_dairy'], 5.29, FALSE);