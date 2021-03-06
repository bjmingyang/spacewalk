-- created by Oraschemadoc Tue Nov  2 08:32:25 2010
-- visit http://www.yarpen.cz/oraschemadoc/ for more info

  CREATE TABLE "SPACEWALK"."QRTZ_SCHEDULER_STATE" 
   (	"INSTANCE_NAME" VARCHAR2(200) NOT NULL ENABLE, 
	"LAST_CHECKIN_TIME" NUMBER(13,0) NOT NULL ENABLE, 
	"CHECKIN_INTERVAL" NUMBER(13,0) NOT NULL ENABLE, 
	 PRIMARY KEY ("INSTANCE_NAME")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS"  ENABLE
   ) PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS" 
 
/
