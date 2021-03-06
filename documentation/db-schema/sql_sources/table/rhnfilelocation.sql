-- created by Oraschemadoc Tue Nov  2 08:32:33 2010
-- visit http://www.yarpen.cz/oraschemadoc/ for more info

  CREATE TABLE "SPACEWALK"."RHNFILELOCATION" 
   (	"FILE_ID" NUMBER NOT NULL ENABLE, 
	"LOCATION" VARCHAR2(128) NOT NULL ENABLE, 
	 CONSTRAINT "RHN_FILELOC_FID_FK" FOREIGN KEY ("FILE_ID")
	  REFERENCES "SPACEWALK"."RHNFILE" ("ID") ENABLE
   ) PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS" ENABLE ROW MOVEMENT 
 
/
