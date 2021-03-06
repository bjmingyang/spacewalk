-- created by Oraschemadoc Tue Nov  2 08:32:46 2010
-- visit http://www.yarpen.cz/oraschemadoc/ for more info

  CREATE TABLE "SPACEWALK"."RHN_COMMAND_QUEUE_SESSIONS" 
   (	"CONTACT_ID" NUMBER(12,0) NOT NULL ENABLE, 
	"SESSION_ID" VARCHAR2(255), 
	"EXPIRATION_DATE" DATE, 
	"LAST_UPDATE_USER" VARCHAR2(40), 
	"LAST_UPDATE_DATE" DATE, 
	 CONSTRAINT "RHN_CQSES_CNTCT_CONTACT_IDFK" FOREIGN KEY ("CONTACT_ID")
	  REFERENCES "SPACEWALK"."WEB_CONTACT" ("ID") ENABLE
   ) PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS" ENABLE ROW MOVEMENT 
 
/
