-- Day 3：初始化 Scania APS 项目数据库
-- 只创建数据库并切换上下文，不导入数据，不写入任何真实密码。

CREATE DATABASE IF NOT EXISTS scania_aps_project
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE scania_aps_project;
