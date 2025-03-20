from dataclasses import dataclass, field


@dataclass
class CSTag:
    code: str
    name: str

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items()}


@dataclass
class BaseArXivCSTags:
    AI: CSTag = field(default_factory=lambda: CSTag("cs.AI", "Artificial Intelligence"))
    AR: CSTag = field(default_factory=lambda: CSTag("cs.AR", "Hardware Architecture"))
    CC: CSTag = field(default_factory=lambda: CSTag("cs.CC", "Computational Complexity"))
    CE: CSTag = field(default_factory=lambda: CSTag("cs.CE", "Computational Engineering, Finance, and Science"))
    CG: CSTag = field(default_factory=lambda: CSTag("cs.CG", "Computational Geometry"))
    CL: CSTag = field(default_factory=lambda: CSTag("cs.CL", "Computation and Language"))
    CR: CSTag = field(default_factory=lambda: CSTag("cs.CR", "Cryptography and Security"))
    CV: CSTag = field(default_factory=lambda: CSTag("cs.CV", "Computer Vision and Pattern Recognition"))
    CY: CSTag = field(default_factory=lambda: CSTag("cs.CY", "Computers and Society"))
    DB: CSTag = field(default_factory=lambda: CSTag("cs.DB", "Databases"))
    DC: CSTag = field(default_factory=lambda: CSTag("cs.DC", "Distributed, Parallel, and Cluster Computing"))
    DL: CSTag = field(default_factory=lambda: CSTag("cs.DL", "Digital Libraries"))
    DM: CSTag = field(default_factory=lambda: CSTag("cs.DM", "Discrete Mathematics"))
    DS: CSTag = field(default_factory=lambda: CSTag("cs.DS", "Data Structures and Algorithms"))
    ET: CSTag = field(default_factory=lambda: CSTag("cs.ET", "Emerging Technologies"))
    FL: CSTag = field(default_factory=lambda: CSTag("cs.FL", "Formal Languages and Automata Theory"))
    GL: CSTag = field(default_factory=lambda: CSTag("cs.GL", "General Literature"))
    GR: CSTag = field(default_factory=lambda: CSTag("cs.GR", "Graphics"))
    GT: CSTag = field(default_factory=lambda: CSTag("cs.GT", "Computer Science and Game Theory"))
    HC: CSTag = field(default_factory=lambda: CSTag("cs.HC", "Human-Computer Interaction"))
    IR: CSTag = field(default_factory=lambda: CSTag("cs.IR", "Information Retrieval"))
    IT: CSTag = field(default_factory=lambda: CSTag("cs.IT", "Information Theory"))
    LG: CSTag = field(default_factory=lambda: CSTag("cs.LG", "Machine Learning"))
    LO: CSTag = field(default_factory=lambda: CSTag("cs.LO", "Logic in Computer Science"))
    MA: CSTag = field(default_factory=lambda: CSTag("cs.MA", "Multiagent Systems"))
    MM: CSTag = field(default_factory=lambda: CSTag("cs.MM", "Multimedia"))
    MS: CSTag = field(default_factory=lambda: CSTag("cs.MS", "Mathematical Software"))
    NA: CSTag = field(default_factory=lambda: CSTag("cs.NA", "Numerical Analysis"))
    NE: CSTag = field(default_factory=lambda: CSTag("cs.NE", "Neural and Evolutionary Computing"))
    NI: CSTag = field(default_factory=lambda: CSTag("cs.NI", "Networking and Internet Architecture"))
    OH: CSTag = field(default_factory=lambda: CSTag("cs.OH", "Other Computer Science"))
    OS: CSTag = field(default_factory=lambda: CSTag("cs.OS", "Operating Systems"))
    PF: CSTag = field(default_factory=lambda: CSTag("cs.PF", "Performance"))
    PL: CSTag = field(default_factory=lambda: CSTag("cs.PL", "Programming Languages"))
    RO: CSTag = field(default_factory=lambda: CSTag("cs.RO", "Robotics"))
    SC: CSTag = field(default_factory=lambda: CSTag("cs.SC", "Symbolic Computation"))
    SD: CSTag = field(default_factory=lambda: CSTag("cs.SD", "Sound"))
    SE: CSTag = field(default_factory=lambda: CSTag("cs.SE", "Software Engineering"))
    SI: CSTag = field(default_factory=lambda: CSTag("cs.SI", "Social and Information Networks"))
    SY: CSTag = field(default_factory=lambda: CSTag("cs.SY", "Systems and Control"))

    def to_dict(self):
        return {key: value.to_dict() for key, value in self.__dict__.items()}


@dataclass
class ArxivTags:
    AI: CSTag = field(default_factory=lambda: CSTag("cs.AI", "Artificial Intelligence"))
    MA: CSTag = field(default_factory=lambda: CSTag("cs.MA", "Multiagent Systems"))
    LG: CSTag = field(default_factory=lambda: CSTag("cs.LG", "Machine Learning"))
    CL: CSTag = field(default_factory=lambda: CSTag("cs.CL", "Computation and Language"))
    IR: CSTag = field(default_factory=lambda: CSTag("cs.IR", "Information Retrieval"))
    NE: CSTag = field(default_factory=lambda: CSTag("cs.NE", "Neural and Evolutionary Computing"))
    SE: CSTag = field(default_factory=lambda: CSTag("cs.SE", "Software Engineering"))

    def to_dict(self):
        return {key: value.to_dict() for key, value in self.__dict__.items()}


@dataclass
class Paper:
    title: str
    pdf_id: str
    tag: str
    all_tags: list
    pdf_url: str = ""
    abs_url: str = ""
    html_url: str = ""

    def __post_init__(self):
        self.pdf_url = f"https://arxiv.org/pdf/{self.pdf_id}"
        self.abs_url = f"https://arxiv.org/abs/{self.pdf_id}"
        self.html_url = f"https://arxiv.org/html/{self.pdf_id}"

    def __hash__(self):
        return hash(self.title)

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items()}
