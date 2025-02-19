CREATE TABLE IF NOT EXISTS `boards` (
    `board_id`              int(11)  	   NOT NULL auto_increment	  COMMENT 'the id of this board',
    `owner_id`              int(11)  	   NOT NULL                   COMMENT 'the user id of the owner of this board',
    `board_name`            varchar(100)   NOT NULL            		  COMMENT 'the name of the board',
PRIMARY KEY (`board_id`),
FOREIGN KEY (owner_id) REFERENCES users(user_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Stores the information for each board";
