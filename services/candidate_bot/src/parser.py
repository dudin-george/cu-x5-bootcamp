"""Resume PDF parser with validation."""

import logging
import re

import pdfplumber

logger = logging.getLogger(__name__)


class ResumeParser:
    """Parse PDF resume and extract candidate data."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = self._extract_text()

    def _extract_text(self) -> str:
        """Extract all text from PDF."""
        text = ""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
        return text
    
    def validate_content(self) -> bool:
        """Check if content looks like a resume.
        
        Returns:
            True if it looks like a resume.
        """
        if not self.text or len(self.text) < 50:
            return False

        text_lower = self.text.lower()
        
        # Keywords typically found in resumes
        keywords = [
            "резюме", "cv", "образование", "опыт работы", "навыки", 
            "skills", "education", "experience", "contacts", "контакты",
            "телефон", "email", "почта", "гражданство", "родился", "рождения"
        ]
        
        found_count = sum(1 for word in keywords if word in text_lower)
        
        if found_count >= 2:
            return True
            
        # Fallback: check for year + contact
        has_year = bool(re.search(r'\b(19|20)\d{2}\b', self.text))
        has_contact = (self.get_email() is not None) or (self.get_phone() is not None)
        
        return has_year and has_contact

    def get_email(self) -> str | None:
        """Find first email address."""
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', self.text)
        return match.group(0) if match else None

    def get_phone(self) -> str | None:
        """Find phone number."""
        pattern = r'(\+7|8)[\s\(-]*\d{3}[\s\)-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}'
        match = re.search(pattern, self.text)
        return match.group(0) if match else None

    def get_links(self) -> str | None:
        """Find resume/portfolio links."""
        urls = re.findall(r'https?://[^\s]+', self.text)
        priority_domains = ['github.com', 'hh.ru', 'linkedin.com', 't.me']
        
        for url in urls:
            if any(domain in url for domain in priority_domains):
                return url
        
        return urls[0] if urls else None

    def get_birth_year(self) -> str | None:
        """Find birth year (19xx or 20xx)."""
        matches = re.findall(r'\b(19\d{2}|20\d{2})\b', self.text)
        valid_years = [int(y) for y in matches if 1970 <= int(y) <= 2010]
        if valid_years:
            return str(min(valid_years))
        return None

    def guess_name(self) -> str | None:
        """Heuristic: take first line as full name."""
        lines = [line.strip() for line in self.text.split('\n') if line.strip()]
        if lines:
            candidate = lines[0]
            words = candidate.split()
            if 1 <= len(words) <= 4:
                return candidate
        return None

    def find_course(self) -> str | None:
        """Find education course/year."""
        current_year = 2025
        
        # Look for year ranges like "2021 - 2025"
        year_matches = re.findall(r'(20\d{2})\s*[-—]\s*(20\d{2}|наст|н\.в)', self.text)
        
        for start_year, end_year_raw in year_matches:
            try:
                start = int(start_year)
                if end_year_raw.isdigit():
                    end = int(end_year_raw)
                    if end >= current_year:
                        course = current_year - start + 1
                        if 1 <= course <= 4:
                            return f"{course} курс (бакалавриат, специалитет)"
                        if 5 <= course <= 6:
                            return f"{course} курс (специалитет)"
                elif "наст" in end_year_raw.lower() or "н.в" in end_year_raw.lower():
                    course = current_year - start + 1
                    if 1 <= course <= 4:
                        return f"{course} курс (бакалавриат, специалитет)"
                    if 5 <= course <= 6:
                        return f"{course} курс (специалитет)"
            except ValueError:
                continue

        # Fallback: look for "N курс"
        match = re.search(r'(\d)\s*курс', self.text, re.IGNORECASE)
        if match:
            return f"{match.group(1)} курс"
        
        if "магистратура" in self.text.lower():
            return "1 курс (магистратура)"
            
        if "бакалавр" in self.text.lower() or "специалист" in self.text.lower():
            return "3 курс (бакалавриат, специалитет)"

        return None

    def find_university(self, known_universities: list[str]) -> str | None:
        """Find university from known list."""
        text_lower = self.text.lower()
        sorted_univs = sorted(known_universities, key=len, reverse=True)
        
        for univ in sorted_univs:
            if univ.lower() in text_lower:
                return univ
        
        # Look for abbreviations
        if "университет" in text_lower or "институт" in text_lower:
            common_abbrs = ["МГУ", "ВШЭ", "МФТИ", "СПбГУ", "ИТМО", "МГТУ", "НИУ ВШЭ"]
            for abbr in common_abbrs:
                if abbr in self.text:
                    return abbr
        
        return None
    
    def find_specialty(self) -> str | None:
        """Find specialty/faculty."""
        patterns = [
            r'Факультет[:\s]+([^\n]+)',
            r'Специальность[:\s]+([^\n]+)',
            r'Направление[:\s]+([^\n]+)',
            r'Образовательная программа[:\s]+([^\n]+)'
        ]
        for p in patterns:
            match = re.search(p, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def find_city(self) -> str | None:
        """Find city."""
        cities = ["Москва", "Санкт-Петербург", "Казань", "Екатеринбург", "Новосибирск"]
        text_lower = self.text.lower()
        for city in cities:
            if city.lower() in text_lower:
                return city
        return None

    def find_citizenship(self) -> str | None:
        """Find citizenship."""
        if "гражданство: рф" in self.text.lower() or "россия" in self.text.lower():
            return "РФ"
        return None

    def find_tech_stack(self) -> str | None:
        """Find technologies."""
        common_tech = [
            "Python", "Java", "C++", "C#", "Go", "Golang", "JavaScript", "TypeScript", 
            "React", "Vue", "Angular", "Docker", "Kubernetes", "SQL", "PostgreSQL", 
            "MySQL", "MongoDB", "Redis", "Git", "Linux", "Bash", "CI/CD", "Django", 
            "FastAPI", "Flask", "Spring", ".NET", "ML", "AI", "Data Science"
        ]
        
        text_split = re.split(r'[\s,;]+', self.text)
        text_tokens = set(t.strip("().,").lower() for t in text_split)

        found = [tech for tech in common_tech if tech.lower() in text_tokens]
        
        return ", ".join(found) if found else None

    def guess_priority(self, tech_stack_str: str | None) -> str | None:
        """Guess priority based on tech stack."""
        if not tech_stack_str:
            return None
        
        stack = tech_stack_str.lower()
        scores = {"frontend": 0, "backend": 0, "analyst": 0}
        
        if any(x in stack for x in ['react', 'vue', 'angular', 'javascript', 'css', 'html']):
            scores["frontend"] += 1
        if any(x in stack for x in ['python', 'java', 'go', 'docker', 'sql', 'django', 'fastapi', 'spring']):
            scores["backend"] += 1
        if any(x in stack for x in ['pandas', 'numpy', 'sql', 'tableau', 'powerbi', 'data']):
            scores["analyst"] += 1
            
        best = max(scores, key=scores.get)
        if scores[best] > 0:
            return best
        return None

    def parse_all(self, universities_list: list[str] | None = None) -> dict:
        """Parse all data from resume.
        
        Args:
            universities_list: Known universities for matching.
            
        Returns:
            Extracted data dict.
        """
        univ_list = universities_list or []
        
        full_name = self.guess_name()
        surname, name = None, None
        if full_name:
            parts = full_name.split()
            if len(parts) >= 2:
                surname = parts[0]
                name = " ".join(parts[1:])
            else:
                surname = full_name 
        
        tech_stack = self.find_tech_stack()
        priority = self.guess_priority(tech_stack)
        
        return {
            "surname": surname,
            "name": name,
            "phone": self.get_phone(),
            "email": self.get_email(),
            "resume_link": self.get_links(), 
            "course": self.find_course(),
            "university": self.find_university(univ_list),
            "specialty": self.find_specialty(),
            "city": self.find_city(),
            "birth_year": self.get_birth_year(),
            "citizenship": self.find_citizenship(),
            "tech_stack": tech_stack,
            "priority": priority,
        }

