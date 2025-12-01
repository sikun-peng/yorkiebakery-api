-- ================================================
-- Music Track Migration
-- Inserts all music entries scraped from static site
-- ================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- PIANO
INSERT INTO music_track (id, title, composer, performer, category, description, file_url, cover_url, uploaded_at)
VALUES
(uuid_generate_v4(), 'Prelude in C Major, No.1, BWV 846', 'Bach, Johann', 'Oscar Peng', 'piano', '赋格', 'https://d2pdj881wm30p5.cloudfront.net/music/Bach_prelude_846.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_langlang.jpg', NOW()),
(uuid_generate_v4(), 'Intermezzo in A major, Op.118 No.2', 'Brahms, Johannes', 'Oscar Peng', 'piano', '反正我的曲子，都是写给你的', 'https://d2pdj881wm30p5.cloudfront.net/music/Brahms_op_118.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_brahms.jpg', NOW()),
(uuid_generate_v4(), 'Barcarolle in F-sharp major, Op.60', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '船歌', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_barcarolle.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_martha_argerich.jpg', NOW()),
(uuid_generate_v4(), 'Ballade No.1 in G minor, Op.23', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '叙一', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_ballade_no_1.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_martha_argerich.jpg', NOW()),
(uuid_generate_v4(), 'Nocturne in B-flat minor, Op.9 No.1', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '降B小调夜曲', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_nocturne_op_9_no_1.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_chopin_1.jpg', NOW()),
(uuid_generate_v4(), 'Nocturne in E-flat major, Op.9 No.2', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '降E大调夜曲', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_nocturne_op_9_no_2.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_chopin_1.jpg', NOW()),
(uuid_generate_v4(), 'Nocturne No.20 in C-sharp minor', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '夜曲第20号', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_nocturne_op_20.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_chopin_1.jpg', NOW()),
(uuid_generate_v4(), 'Nocturne in C minor, Op.48 No.1', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '夜曲48之1', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_nocturne_op_48_no_1.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_chopin_1.jpg', NOW()),
(uuid_generate_v4(), 'Nocturne in E minor, Op.72 No.1', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '夜曲72之1', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_nocturne_op_72_no_1.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_chopin_1.jpg', NOW()),
(uuid_generate_v4(), 'Piano Concerto No.1 in E minor, Op.11', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '肖一', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_1st_concerto.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_bruce_liu_concerto.jpg', NOW()),
(uuid_generate_v4(), 'Scherzo in B-flat minor, Op.31', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '谐2', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_scherzo_no_2.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_chopin_1.jpg', NOW()),
(uuid_generate_v4(), 'Waltz in E-flat major, Op.18', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '华丽大圆舞曲', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_waltzes_op.18.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_alice_sara_waltz.jpg', NOW()),
(uuid_generate_v4(), 'Waltz in D-flat major, Op.64 No.1', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '小狗圆舞曲', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_alice_sara_waltz.jpg', NOW()),
(uuid_generate_v4(), 'Waltz in B minor, Op.69 No.2', 'Chopin, Frédéric', 'Oscar Peng', 'piano', 'b小调华尔兹', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_waltzes_op_69_no_2.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_alice_sara_waltz.jpg', NOW()),
(uuid_generate_v4(), 'Waltz in G-flat major, Op.70 No.1', 'Chopin, Frédéric', 'Oscar Peng', 'piano', 'G大调华尔兹', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_alice_sara_waltz.jpg', NOW()),
(uuid_generate_v4(), 'Fantasy-Impromptu, Op.66', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '幻想即兴曲', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_fantaisie_impromptu.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_martha_argerich.jpg', NOW()),
(uuid_generate_v4(), 'Etude in C minor, Op.10 No.12', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '革命练习曲', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_bruce_liu_etude.jpg', NOW()),
(uuid_generate_v4(), 'Etude in A-flat major, Op.25 No.1', 'Chopin, Frédéric', 'Oscar Peng', 'piano', 'The most beautiful etude ever', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_bruce_liu_etude.jpg', NOW()),
(uuid_generate_v4(), 'Etude in B minor, Op.25 No.10', 'Chopin, Frédéric', 'Oscar Peng', 'piano', 'Octaves', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_bruce_liu_etude.jpg', NOW()),
(uuid_generate_v4(), 'Prelude in D-flat major, Op.28 No.15', 'Chopin, Frédéric', 'Oscar Peng', 'piano', '雨滴前奏曲', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_prelude_op_28_no_15.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_martha_argerich.jpg', NOW()),
(uuid_generate_v4(), 'Arabesque No.1', 'Debussy, Claude', 'Oscar Peng', 'piano', '阿拉伯风格曲', 'https://d2pdj881wm30p5.cloudfront.net/music/Debussy_arabesque_no_1.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_debussy.jpg', NOW()),
(uuid_generate_v4(), 'Beau Soir', 'Debussy, Claude', 'Oscar Peng', 'piano', 'dream / 梦', 'https://d2pdj881wm30p5.cloudfront.net/music/Debussy_beau_soir.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_debussy.jpg', NOW()),
(uuid_generate_v4(), 'Clair de Lune', 'Debussy, Claude', 'Oscar Peng', 'piano', '月光', 'https://d2pdj881wm30p5.cloudfront.net/music/Debussy_claude_clair_lune.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_debussy.jpg', NOW()),
(uuid_generate_v4(), 'Rêverie', 'Debussy, Claude', 'Oscar Peng', 'piano', '', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_debussy.jpg', NOW()),
(uuid_generate_v4(), 'Albumblatt in Walzer-Form', 'Liszt, Franz', 'Oscar Peng', 'piano', 'A cute piece from Liszt', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_liszt.jpg', NOW()),
(uuid_generate_v4(), 'Liebesträume No.3', 'Liszt, Franz', 'Oscar Peng', 'piano', '爱之梦', 'https://d2pdj881wm30p5.cloudfront.net/music/Liszt_liebestraum_no_3.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_liszt.jpg', NOW()),
(uuid_generate_v4(), 'Piano Sonata in B minor, S.178', 'Liszt, Franz', 'Oscar Peng', 'piano', '李b', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_liszt.jpg', NOW()),
(uuid_generate_v4(), 'Liebesleid', 'Rachmaninoff, Sergei', 'Oscar Peng', 'piano', '爱的悲伤', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_rachmaninoff.jpg', NOW()),
(uuid_generate_v4(), 'Piano Concerto No.2 in C minor, Op.18', 'Rachmaninoff, Sergei', 'Oscar Peng', 'piano', '拉二', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_rachmaninoff.jpg', NOW()),
(uuid_generate_v4(), 'Piano Concerto No.3 in D minor, Op.30', 'Rachmaninoff, Sergei', 'Oscar Peng', 'piano', '拉三', 'https://d2pdj881wm30p5.cloudfront.net/music/Rachmaninoff_piano_concerto_no_3.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_yunchan_lim_rach.jpg', NOW()),
(uuid_generate_v4(), 'Rhapsody on a Theme of Paganini, Var.18', 'Rachmaninoff, Sergei', 'Oscar Peng', 'piano', '帕格尼尼主题第18变奏', 'https://d2pdj881wm30p5.cloudfront.net/music/Rachmaninoff _var_18.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_rachmaninoff.jpg', NOW()),
(uuid_generate_v4(), 'Salut d''Amour', 'Elgar, Edward', 'Oscar Peng', 'piano', '爱的礼赞', 'https://d2pdj881wm30p5.cloudfront.net/music/Elgar_love_s_greeting_piano.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_髙木凜々子_3.jpg', NOW()),
(uuid_generate_v4(), 'Sonata in E Major K.380', 'Scarlatti, Domenico', 'Oscar Peng', 'piano', '小清新', 'https://d2pdj881wm30p5.cloudfront.net/music/Scarlatti_sonata_k380.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_scarlatti.jpg', NOW()),
(uuid_generate_v4(), 'Ständchen (Serenade)', 'Schubert, Franz', 'Oscar Peng', 'piano', '小夜曲', 'https://d2pdj881wm30p5.cloudfront.net/music/Schubert_serenade_piano.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_schubert.jpg', NOW()),
(uuid_generate_v4(), 'Abegg Variations, Op.1', 'Schumann, Robert', 'Oscar Peng', 'piano', '阿贝格变奏曲', 'https://d2pdj881wm30p5.cloudfront.net/music/Shumann_abegg_variation_op_1.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_schumann.jpg', NOW()),
(uuid_generate_v4(), 'Papillons, Op.2', 'Schumann, Robert', 'Oscar Peng', 'piano', '蝴蝶', 'https://d2pdj881wm30p5.cloudfront.net/music/Schumann_papillons_op_2.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_schumann.jpg', NOW()),
(uuid_generate_v4(), 'Von fremden Ländern und Menschen', 'Schumann, Robert', 'Oscar Peng', 'piano', 'Oscar最喜欢的舒曼曲', 'https://d2pdj881wm30p5.cloudfront.net/music/Schumann_von_fremden.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_schumann.jpg', NOW()),
(uuid_generate_v4(), 'Träumerei, Op.15 No.7', 'Schumann, Robert', 'Oscar Peng', 'piano', '梦幻曲', 'https://d2pdj881wm30p5.cloudfront.net/music/Schumann_traumerei.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_schumann.jpg', NOW());


-- VIOLIN
INSERT INTO music_track (id, title, composer, performer, category, description, file_url, cover_url, uploaded_at)
VALUES
(uuid_generate_v4(), 'Violin Concerto No. 1 in A minor, Op.99', 'Shostakovich, Dmitri', 'Oscar Peng', 'violin', '老肖一', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_shostakovich.jpg', NOW()),
(uuid_generate_v4(), 'Violin Concerto in D minor, Op.47', 'Sibelius, Jean ', 'Oscar Peng', 'violin', '柴小协', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_sibelius.jpg', NOW());

-- ACCOMPANIMENT
INSERT INTO music_track (id, title, composer, performer, category, description, file_url, cover_url, uploaded_at)
VALUES
(uuid_generate_v4(), 'Violin Sonata no.3 in E-flat, Op.12, No.3', 'Beethoven, Ludwig van', 'Weronika Dziadek', 'accompaniment', '', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_maría_dueñas.jpg', NOW()),
(uuid_generate_v4(), 'Violin Sonata No.5 in F major, Op.24', 'Beethoven, Ludwig van', 'Weronika Dziadek', 'accompaniment', '春天奏鸣曲', 'https://d2pdj881wm30p5.cloudfront.net/music/Beethoven_violin_sonata_no_5.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_maría_dueñas.jpg', NOW()),
(uuid_generate_v4(), 'Contemplation, Op. 105, No. 1 for Violin and Piano', 'Brahms, Johannes', '荒井里桜', 'accompaniment', '', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_荒井里桜.jpg', NOW()),
(uuid_generate_v4(), 'Salut d''Amour', 'Elgar, Edward', '島谷美賀子', 'accompaniment', 'Love''s Greeting / 爱的礼赞', 'https://d2pdj881wm30p5.cloudfront.net/music/Elgar_love_s_greeting_violin.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_髙木凜々子_3.jpg', NOW()),
(uuid_generate_v4(), 'Liebesleid', 'Kreisler, Fritz', 'Joshua Bell', 'accompaniment', '爱的悲伤', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_joshua_bell.jpg', NOW()),
(uuid_generate_v4(), 'Song Without Words, Op.62', 'Mendelssohn, Felix', 'Tiffany', 'accompaniment', 'Spring Song', '', NULL, NOW()),
(uuid_generate_v4(), 'Carmen Fantasy, Op.25', 'Sarasate, Pablo de', 'SoHyun Ko', 'accompaniment', '', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_髙木凜々子_1.jpg', NOW()),
(uuid_generate_v4(), 'Introduction and Tarantella, Op.43', 'Sarasate, Pablo de', 'Maxim Vengerov', 'accompaniment', '', 'https://d2pdj881wm30p5.cloudfront.net/music/Sarasata_introduction_and_tarantelle.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_髙木凜々子_2.jpg', NOW()),
(uuid_generate_v4(), 'Zigeunerweisen Op.20', 'Sarasate, Pablo de', 'SoHyun Ko', 'accompaniment', '', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_髙木凜々子_2.jpg', NOW()),
(uuid_generate_v4(), 'Ständchen (cello)', 'Schubert, Franz', 'Camille Thomas', 'accompaniment', '', 'https://d2pdj881wm30p5.cloudfront.net/music/Schubert_serenade_cello.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_schubert.jpg', NOW()),
(uuid_generate_v4(), 'Ständchen (vocal)', 'Schubert, Franz', 'Park Nouri', 'accompaniment', '', 'https://d2pdj881wm30p5.cloudfront.net/music/Schubert_serenade_vocal.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_schubert.jpg', NOW()),
(uuid_generate_v4(), 'Ständchen (violin)', 'Schubert, Franz', 'Tiffany', 'accompaniment', '', 'https://d2pdj881wm30p5.cloudfront.net/music/Schubert_serenade_violin.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_schubert.jpg', NOW()),
(uuid_generate_v4(), 'Widmung, Op.25 No.1', 'Schumann, Robert', 'Maryam Wocial', 'accompaniment', '爱的献礼', 'https://d2pdj881wm30p5.cloudfront.net/music/Schumann_widmung.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_schumann.jpg', NOW());

-- UPCOMING LIST
INSERT INTO music_track (id, title, composer, performer, category, description, file_url, cover_url, uploaded_at)
VALUES
(uuid_generate_v4(), 'Andante Spianato & Grande Polonaise Brillante, Op.22', 'Chopin, Frédéric', 'Oscar Peng', 'upcoming', '华丽的大波兰舞曲之行板', 'https://d2pdj881wm30p5.cloudfront.net/music/Chopin_grande_polonaise_brillante.mp3', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_chopin_2.jpg', NOW()),
(uuid_generate_v4(), 'Ballade No.2 in F major, Op.38', 'Chopin, Frédéric', 'Oscar Peng', 'upcoming', '', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_chopin_2.jpg', NOW()),
(uuid_generate_v4(), 'Ballade No.4 in F minor, Op.52', 'Chopin, Frédéric', 'Oscar Peng', 'upcoming', '', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_chopin_2.jpg', NOW()),
(uuid_generate_v4(), 'Etudes Op.25 No.11', 'Chopin, Frédéric', 'Oscar Peng', 'upcoming', '冬风', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_yunchan_lim_chopin.jpg', NOW()),
(uuid_generate_v4(), 'Etudes Op.25 No.12', 'Chopin, Frédéric', 'Oscar Peng', 'upcoming', 'Ocean / 大海', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_yunchan_lim_chopin.jpg', NOW()),
(uuid_generate_v4(), 'Waltz Op.42', 'Chopin, Frédéric', 'Oscar Peng', 'upcoming', 'Two Four Waltz', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_alice_sara_waltz.jpg', NOW());

-- WISHLIST
INSERT INTO music_track (id, title, composer, performer, category, description, file_url, cover_url, uploaded_at)
VALUES
(uuid_generate_v4(), 'Piano Concerto No.2 in C minor, Op.18', 'Rachmaninoff, Sergei', 'Oscar Peng', 'wishlist', '拉二', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_rachmaninoff.jpg', NOW()),
(uuid_generate_v4(), 'Polonaise in F-sharp minor, Op.44', 'Chopin, Frédéric', 'Oscar Peng', 'wishlist', 'F小调波兰舞曲', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_chopin_2.jpg', NOW()),
(uuid_generate_v4(), 'Impromptu in E-flat major, Op.90 No.2', 'Schubert, Franz', 'Oscar Peng', 'wishlist', '降E大调即兴曲', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_schubert.jpg', NOW()),
(uuid_generate_v4(), 'La Campanella', 'Liszt, Franz', 'Oscar Peng', 'wishlist', '钟', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_liszt.jpg', NOW()),
(uuid_generate_v4(), 'Hungarian Rhapsody No.2', 'Liszt, Franz', 'Oscar Peng', 'wishlist', '匈牙利狂想曲第二号', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_liszt.jpg', NOW()),
(uuid_generate_v4(), 'Mephisto Waltz No.1', 'Liszt, Franz', 'Oscar Peng', 'wishlist', '梅菲斯特圆舞曲', '', 'https://d2pdj881wm30p5.cloudfront.net/music-covers/cover_liszt.jpg', NOW());