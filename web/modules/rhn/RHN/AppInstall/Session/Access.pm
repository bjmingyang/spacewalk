#
# Copyright (c) 2008 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
# 
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation. 
#

package RHN::AppInstall::Session::Access;

use strict;
use RHN::Exception qw/throw/;
use PXT::ACL;

sub register_acl_handlers {
  my $self = shift;
  my $acl = shift;

  $acl->register_handler(session_data_true => \&session_data_true);
}

sub session_data_true {
  my $session = shift;
  my $param = shift;

  throw "(no_data) No param name to test against" unless $param;

  return $session->param($param) ? 1 : 0;
}

1;
