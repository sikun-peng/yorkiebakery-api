-- migrations/007_update_macarons_gallery.sql
UPDATE menu_item
SET gallery_urls = ARRAY[
  'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/macarons_1.jpg',
  'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/macarons_2.jpg',
  'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/macarons_3.jpg',
  'https://yorkiebakery-image.s3.us-west-2.amazonaws.com/menu/macarons_4.jpg'
]
WHERE title = 'Macarons';
