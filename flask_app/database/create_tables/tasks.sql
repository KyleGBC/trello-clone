CREATE TABLE IF NOT EXISTS `tasks` (
    `task_id`               int(11)  	   NOT NULL auto_increment	  COMMENT 'the id of this task',
    `board_id`              int(11)  	   NOT NULL                   COMMENT 'the id of the board this task belongs to',
    `status`                varchar(100)   NOT NULL            		  COMMENT 'the status of the task. can be "to do", "in progress", "done"',
    `name`                  varchar(100)   NOT NULL            		  COMMENT 'the name of the task',
    `description`           varchar(1000)  NOT NULL            		  COMMENT 'the description of the task',
    `order`                 int(11)        NOT NULL                   COMMENT 'the order of the task in the board',
PRIMARY KEY (`task_id`),
FOREIGN KEY (board_id) REFERENCES boards(board_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Stores the information for each task";