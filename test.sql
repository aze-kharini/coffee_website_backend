INSERT INTO users (user_id, password,mail, user_type)
VALUES ('admin',  'pbkdf2:sha256:260000$BM6ykxAVq9jYAVW0$ced2ec642fbb06ea1ac969d334076854033bfe532f4b0cbf66ddaf6f8e2af541','admin@example.com', 'admin'),
('expert',  'pbkdf2:sha256:260000$DkxGQsMlM9R0r9mT$6af306683f69403d9ed04824cbf3a2d6545f839d583de67b7a1079bdcb88eb79','expert@example.com', 'expert');

-- SELECT * FROM genetic_relations;