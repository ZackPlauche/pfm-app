from __future__ import annotations

from decimal import Decimal
import csv
from typing import Literal
from datetime import datetime, date as datetime_date
from pathlib import Path

import pandas as pd
from pydantic import Field, field_serializer, BaseModel
from dataclasses import dataclass



class Account(BaseModel):
    number: str
    bank: str
    type: Literal['checking', 'savings', 'credit']  # What type of account it is
    transactions: list[Transaction] = Field(default_factory=list)

    def __str__(self):
        return f'{self.bank} {self.type.capitalize()} account ending in {self.number}'

    @classmethod
    def from_chase_account_activity(cls, file_path: str | Path, type: Literal['checking', 'savings', 'credit']):
        file_path = Path(file_path)
        account = cls(bank='Chase', number=file_path.stem[5:9], type=type)
        with file_path.open('r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                _, date_str, description, amount_str, *_ = row
                account.transactions.append(
                    Transaction(
                        description=description,
                        amount=amount_str,
                        date=datetime.strptime(date_str, '%m/%d/%Y').date(),
                        account=account,
                    )
                )
        return account
    
    def to_df(self) -> pd.DataFrame:
        df = pd.DataFrame(self.model_dump()['transactions'])
        df.rename(columns={'date': 'Date', 'description': 'Description', 'amount': 'Amount'}, inplace=True)
        # Reorder columns to Date, Amount, Description
        df = df[['Date', 'Amount', 'Description']]
        return df


    @field_serializer('transactions')
    def serialize_without_circular_ref(transactions: list[Transaction]):
        return [transaction.model_dump(exclude={'account'}) for transaction in transactions]
    
    def total(self):
        return sum(transaction.amount for transaction in self.transactions)


class Transaction(BaseModel):
    description: str
    amount: Decimal
    date: datetime_date = Field(default_factory=datetime_date.today)
    account: Account = Field(repr=False)

    @field_serializer('account')
    def serialize_without_circular_ref(account: Account):
        return account.model_dump(exclude={'transactions'})



