-- created by Oraschemadoc Tue Nov  2 08:32:37 2010
-- visit http://www.yarpen.cz/oraschemadoc/ for more info

  CREATE TABLE "SPACEWALK"."RHNPACKAGESOURCE" 
   (	"ID" NUMBER NOT NULL ENABLE, 
	"ORG_ID" NUMBER, 
	"SOURCE_RPM_ID" NUMBER NOT NULL ENABLE, 
	"PACKAGE_GROUP" NUMBER NOT NULL ENABLE, 
	"RPM_VERSION" VARCHAR2(16) NOT NULL ENABLE, 
	"PAYLOAD_SIZE" NUMBER NOT NULL ENABLE, 
	"BUILD_HOST" VARCHAR2(256) NOT NULL ENABLE, 
	"BUILD_TIME" DATE NOT NULL ENABLE, 
	"SIGCHECKSUM_ID" NUMBER NOT NULL ENABLE, 
	"VENDOR" VARCHAR2(64) NOT NULL ENABLE, 
	"COOKIE" VARCHAR2(128) NOT NULL ENABLE, 
	"PATH" VARCHAR2(1000), 
	"CHECKSUM_ID" NUMBER NOT NULL ENABLE, 
	"PACKAGE_SIZE" NUMBER NOT NULL ENABLE, 
	"LAST_MODIFIED" DATE DEFAULT (sysdate) NOT NULL ENABLE, 
	"CREATED" DATE DEFAULT (sysdate) NOT NULL ENABLE, 
	"MODIFIED" DATE DEFAULT (sysdate) NOT NULL ENABLE, 
	 CONSTRAINT "RHN_PKGSRC_ID_PK" PRIMARY KEY ("ID")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS"  ENABLE, 
	 CONSTRAINT "RHN_PKGSRC_OID_FK" FOREIGN KEY ("ORG_ID")
	  REFERENCES "SPACEWALK"."WEB_CUSTOMER" ("ID") ON DELETE CASCADE ENABLE, 
	 CONSTRAINT "RHN_PKGSRC_SRID_FK" FOREIGN KEY ("SOURCE_RPM_ID")
	  REFERENCES "SPACEWALK"."RHNSOURCERPM" ("ID") ENABLE, 
	 CONSTRAINT "RHN_PKGSRC_GROUP_FK" FOREIGN KEY ("PACKAGE_GROUP")
	  REFERENCES "SPACEWALK"."RHNPACKAGEGROUP" ("ID") ENABLE, 
	 CONSTRAINT "RHN_PKGSRC_SIGCHSUM_FK" FOREIGN KEY ("SIGCHECKSUM_ID")
	  REFERENCES "SPACEWALK"."RHNCHECKSUM" ("ID") ENABLE, 
	 CONSTRAINT "RHN_PKGSRC_CHSUM_FK" FOREIGN KEY ("CHECKSUM_ID")
	  REFERENCES "SPACEWALK"."RHNCHECKSUM" ("ID") ENABLE
   ) PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS" ENABLE ROW MOVEMENT 
 
/
