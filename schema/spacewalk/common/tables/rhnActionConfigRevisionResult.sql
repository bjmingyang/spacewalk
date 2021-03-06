--
-- Copyright (c) 2008 Red Hat, Inc.
--
-- This software is licensed to you under the GNU General Public License,
-- version 2 (GPLv2). There is NO WARRANTY for this software, express or
-- implied, including the implied warranties of MERCHANTABILITY or FITNESS
-- FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
-- along with this software; if not, see
-- http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
--
-- Red Hat trademarks are not licensed under GPLv2. No permission is
-- granted to use or replicate Red Hat trademarks that are incorporated
-- in this software or its documentation.
--


CREATE TABLE rhnActionConfigRevisionResult
(
    action_config_revision_id  NUMBER NOT NULL
                                   CONSTRAINT rhn_actioncfr_acrid_fk
                                       REFERENCES rhnActionConfigRevision (id)
                                       ON DELETE CASCADE,
    result                     BLOB,
    created                    DATE
                                   DEFAULT (sysdate) NOT NULL,
    modified                   DATE
                                   DEFAULT (sysdate) NOT NULL
)
ENABLE ROW MOVEMENT
;

CREATE UNIQUE INDEX rhn_actioncfr_acrid_uq
    ON rhnActionConfigRevisionResult (action_config_revision_id)
    TABLESPACE [[2m_tbs]];

