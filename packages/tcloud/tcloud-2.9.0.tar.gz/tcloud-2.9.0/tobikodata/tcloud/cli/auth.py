import typing as t

import click

from tobikodata.tcloud.auth import tcloud_sso

SSO = tcloud_sso()


@click.group()
def auth() -> None:
    """
    Tobiko Cloud Authentication
    """


@auth.command()
def status() -> None:
    """Display current session status"""
    SSO.status()


@auth.command(hidden=True)
def token() -> None:
    """Copy the current token onto clipboard"""
    SSO.copy_token()


@auth.command(hidden=True)
@click.option("-u", "--undo", required=False, is_flag=True, help="Remove current impersonation")
@click.option(
    "-o",
    "--org",
    required=False,
    help="The Tobiko org to use",
    default="*",
)
@click.option(
    "-p",
    "--project",
    required=False,
    help="The Tobiko project to use",
    default="*",
)
@click.option(
    "-l",
    "--level",
    required=False,
    type=click.Choice(["viewer", "developer", "admin"], case_sensitive=False),
    help="The permission level to use",
    default="admin",
)
@click.option(
    "-n",
    "--name",
    required=False,
    help="The name to include in the impersonated token",
)
@click.option(
    "-e",
    "--email",
    required=False,
    help="The email to include in the impersonated token",
)
def impersonate(
    undo: bool,
    org: str,
    project: str,
    level: str,
    name: t.Optional[str] = None,
    email: t.Optional[str] = None,
) -> None:
    """Impersonate another user that has a subset of your own permissions"""
    if undo:
        SSO.undo_impersonation()
        return

    SSO.impersonate(scope=f"tbk:scope:project:{org}:{project}:{level}", name=name, email=email)


@auth.command()
def refresh() -> None:
    """Refresh your current token"""
    SSO.refresh_token()


@auth.command()
def logout() -> None:
    """Logout of any current session"""
    SSO.logout()


@auth.command()
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    help="Create a new session even when one already exists.",
)
def login(force: bool) -> None:
    """Login to Tobiko Cloud"""
    SSO.login() if force else SSO.id_token(login=True)
    SSO.status()
