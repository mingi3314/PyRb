from typing import Annotated

from fastapi import Depends

from pyrb.controllers.constants import ACCOUNTS_CONFIG_PATH
from pyrb.repositories.account import AccountRepository, LocalConfigAccountRepository
from pyrb.repositories.brokerages.context import RebalanceContext, create_rebalance_context
from pyrb.services.account import AccountService


def account_repo_dep() -> AccountRepository:
    return LocalConfigAccountRepository(config_path=ACCOUNTS_CONFIG_PATH)


AccountRepoDep = Annotated[AccountRepository, Depends(account_repo_dep)]


def account_service_dep(account_repo: AccountRepoDep) -> AccountService:
    return AccountService(account_repo)


AccountServiceDep = Annotated[AccountService, Depends(account_service_dep)]


def context_dep(account_repo: AccountRepoDep) -> RebalanceContext:
    account = account_repo.get()
    return create_rebalance_context(account)


RebalanceContextDep = Annotated[RebalanceContext, Depends(context_dep)]
