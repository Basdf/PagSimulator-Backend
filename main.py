from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from pagingPolicy import pagingPolicy

app = FastAPI()


class Options(BaseModel):
    addresses: str = Field(description="ADDRESSES a set of comma-separated pages to access; -1 means randomly generate")
    numaddrs: Optional[int] = Field(description="NUMADDRS if addresses is -1, this is the number of addrs to generate (Optional)")
    policy: str = Field(description="POLICY replacement policy: FIFO, LRU, MRU, OPT, UNOPT, RAND, CLOCK")
    clockbits: Optional[int] = Field(description="CLOCKBITS for CLOCK policy, how many clock bits to use (Optional)")
    cachesize: int = Field(description="CACHESIZE size of the page cache, in pages")
    maxpage: Optional[int] = Field(description="MAXPAGE if randomly generating page accesses, this is the max page number (Optional)")
    seed: Optional[int] = Field(description="SEED  random number seed (Optional)")

    class Config:
        schema_extra = {
            "example": {
                "addresses": "1,2,5,6,5,4,1,2,3,5,1,4",
                "numaddrs": "10",
                "policy": "FIFO",
                "clockbits": 2,
                "cachesize": 3,
                "maxpage": 10,
                "seed": 0,
            }
        }


@app.post("/pagingPolicy")
async def pagSimulator(options: Options):
    policyList = ["FIFO", "LRU", "MRU", "OPT", "UNOPT", "RAND", "CLOCK"]

    if not options.policy in policyList:
        return {"Error": "Policy %s is not yet implemented" % options.policy}

    if not "," in options.addresses:
        return {"Error": "Wrong format in addresses"}

    addresses = options.addresses
    policy = options.policy
    cachesize = options.cachesize

    numaddrs = [lambda:options.numaddrs, lambda:10][not options.numaddrs]()
    clockbits = [lambda:options.clockbits, lambda:2][not options.clockbits]()
    maxpage = [lambda:options.maxpage, lambda:10][not options.maxpage]()
    seed = [lambda:options.seed, lambda:0][not options.seed]()

    return pagingPolicy(addresses, numaddrs, policy, clockbits, cachesize, maxpage, seed)
