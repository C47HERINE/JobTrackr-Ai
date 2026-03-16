import time
from threading import Lock
from sqlalchemy import create_engine, Integer, String, Text, select, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class JobList(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    indeed_id: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    link: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    company: Mapped[str] = mapped_column(String(250), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    job_type: Mapped[str | None] = mapped_column(String(250), nullable=True)
    skills: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    should_apply: Mapped[str | None] = mapped_column(String(250), nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    time_stamp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_applied: Mapped[bool | None] = mapped_column(nullable=True, default=False)
    is_hidden: Mapped[bool] = mapped_column(nullable=False, default=False)
    city: Mapped[str | None] = mapped_column(String(250), nullable=True)

class JobRepository:
    def __init__(self):
        self.write_lock = Lock()
        self.engine = create_engine("sqlite:///data/jobs.db", echo=False)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)


    def load_jobs(self) -> list[dict]:
        cutoff = int(time.time()) - (14 * 24 * 60 * 60)
        with self.Session() as session:
            session.execute(
                delete(JobList).where(JobList.time_stamp < cutoff, JobList.is_applied.is_(False))
                )
            session.commit()
            result = session.execute(
                select(JobList).where(JobList.is_hidden.is_(False)).order_by(JobList.time_stamp.desc()))
            return [job.__dict__ for job in result.scalars().all()]


    def _create_job(self, job: dict):
        with self.Session() as session:
            new_job = JobList(
                indeed_id=job['indeed_id'],
                title=job['title'],
                link=job['link'],
                company=job['company'],
                location=job['location'],
                job_type=job['job_type'],
                skills=job['skills'],
                description=job['description'],
                should_apply=job['should_apply'],
                answer=job['answer'],
                time_stamp=job['time_stamp'],
                is_applied=job['is_applied'],
                city=job['city']
            )
            session.add(new_job)
            session.commit()


    def _update_by_indeed_id(self, job: dict):
        with self.Session() as session:
            job_to_update = session.execute(select(JobList).where(JobList.indeed_id == job['indeed_id'])).scalar_one_or_none()
            if job_to_update:
                job_to_update.title = job['title']
                job_to_update.link = job['link']
                job_to_update.company = job['company']
                job_to_update.location = job['location']
                job_to_update.job_type = job['job_type']
                job_to_update.skills = job['skills']
                job_to_update.description = job['description']
                job_to_update.should_apply = job['should_apply']
                job_to_update.answer = job['answer']
                job_to_update.time_stamp = job['time_stamp']
                job_to_update.is_applied = job['is_applied']
                job_to_update.city = job['city']
                session.commit()


    def save_jobs(self, new_jobs: list[dict]):
        with self.write_lock:
            all_jobs = self.load_jobs()
            existing_ids = [job['indeed_id'] for job in all_jobs]
            for job in new_jobs:
                if job["indeed_id"] not in existing_ids:
                    self._create_job(job)
                else:
                    self._update_by_indeed_id(job)


    def save_job(self, job: dict):
        self.save_jobs([job])