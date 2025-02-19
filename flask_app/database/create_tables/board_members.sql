CREATE TABLE IF NOT EXISTS `board_members` (
    `board_id`              int(11)  	   NOT NULL             	  COMMENT 'the id of a board',
    `user_id`               int(11)  	   NOT NULL                   COMMENT 'the id of a member of the board',
FOREIGN KEY (board_id) REFERENCES boards(board_id),
FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Stores which users are members of which boards";
