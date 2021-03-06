-- created by Oraschemadoc Tue Nov  2 08:32:44 2010
-- visit http://www.yarpen.cz/oraschemadoc/ for more info

  CREATE TABLE "SPACEWALK"."RHNUSERGROUP" 
   (	"ID" NUMBER NOT NULL ENABLE, 
	"NAME" VARCHAR2(64) NOT NULL ENABLE, 
	"DESCRIPTION" VARCHAR2(1024) NOT NULL ENABLE, 
	"MAX_MEMBERS" NUMBER, 
	"CURRENT_MEMBERS" NUMBER DEFAULT (0) NOT NULL ENABLE, 
	"GROUP_TYPE" NUMBER NOT NULL ENABLE, 
	"ORG_ID" NUMBER NOT NULL ENABLE, 
	"CREATED" DATE DEFAULT (sysdate) NOT NULL ENABLE, 
	"MODIFIED" DATE DEFAULT (sysdate) NOT NULL ENABLE, 
	 CONSTRAINT "RHN_USER_GROUP_PK" PRIMARY KEY ("ID")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS"  ENABLE, 
	 CONSTRAINT "RHN_UG_OID_GT_UQ" UNIQUE ("ORG_ID", "GROUP_TYPE")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS"  ENABLE, 
	 CONSTRAINT "RHN_USERGROUP_TYPE_FK" FOREIGN KEY ("GROUP_TYPE")
	  REFERENCES "SPACEWALK"."RHNUSERGROUPTYPE" ("ID") ENABLE, 
	 CONSTRAINT "RHN_USER_GROUP_ORG_FK" FOREIGN KEY ("ORG_ID")
	  REFERENCES "SPACEWALK"."WEB_CUSTOMER" ("ID") ON DELETE CASCADE ENABLE
   ) PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS" ENABLE ROW MOVEMENT 
 
/
