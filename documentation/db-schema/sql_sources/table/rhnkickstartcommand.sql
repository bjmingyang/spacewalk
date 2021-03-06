-- created by Oraschemadoc Tue Nov  2 08:32:34 2010
-- visit http://www.yarpen.cz/oraschemadoc/ for more info

  CREATE TABLE "SPACEWALK"."RHNKICKSTARTCOMMAND" 
   (	"ID" NUMBER, 
	"KICKSTART_ID" NUMBER NOT NULL ENABLE, 
	"KS_COMMAND_NAME_ID" NUMBER NOT NULL ENABLE, 
	"ARGUMENTS" VARCHAR2(2048), 
	"CREATED" DATE DEFAULT (sysdate) NOT NULL ENABLE, 
	"MODIFIED" DATE DEFAULT (sysdate) NOT NULL ENABLE, 
	 CONSTRAINT "RHN_KSCOMMAND_ID_PK" PRIMARY KEY ("ID")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS"  ENABLE, 
	 CONSTRAINT "RHN_KSCOMMAND_KSID_FK" FOREIGN KEY ("KICKSTART_ID")
	  REFERENCES "SPACEWALK"."RHNKSDATA" ("ID") ON DELETE CASCADE ENABLE, 
	 CONSTRAINT "RHN_KSCOMMAND_KCNID_FK" FOREIGN KEY ("KS_COMMAND_NAME_ID")
	  REFERENCES "SPACEWALK"."RHNKICKSTARTCOMMANDNAME" ("ID") ENABLE
   ) PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS" ENABLE ROW MOVEMENT 
 
/
