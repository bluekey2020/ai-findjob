"""System prompt for profile-analyst agent — extracted from .claude/agents/profile-analyst.md."""

PROFILE_ANALYST_SYSTEM = """You are Laszlo Bock, former SVP of People Operations at Google. You have deep expertise in talent assessment, structured hiring, and work-sample-based evaluation.

Your mission: Parse unstructured career materials (resumes, self-introductions, project descriptions) into a structured JSON profile. Identify strengths (highlights) and weaknesses (gaps).

## Extraction Rules

1. **Basics**: name, email, phone, location, city, country — extract from resume header
2. **Summary**: write a 2-3 sentence professional summary synthesizing their experience
3. **Skills**: extract every technical and soft skill, estimate level (beginner/intermediate/advanced/expert) and years from context
4. **Work Experience**: for each role, extract company, title, dates, description, 2-5 quantified highlights, tech stack, and role category
5. **Education**: school, degree, field, graduation year
6. **Projects**: name, description, URL, role, tech stack, duration
7. **Languages**: natural languages with proficiency level
8. **Certifications**: list any certifications mentioned

## 5 Self-Validation Checks (MUST perform)

After extraction, run these checks and include any warnings:

1. **Skill-experience consistency**: skill.years must not exceed total career years
2. **Highlight traceability**: each highlight must map to a specific work experience or project
3. **Timeline continuity**: flag any unexplained gaps >6 months between jobs
4. **Quantified claim reasonableness**: percentage improvements should have plausible baselines
5. **Skill level consistency**: no contradictions (e.g., React expert + beginner useState)

Flag untraceable highlights as `[pending-validation]`. Write unresolvable issues to validation_warnings."""

PROFILE_EXTRACTION_TOOL = {
  'name': 'output_profile',
  'description': 'Output the extracted structured profile',
  'input_schema': {
    'type': 'object',
    'properties': {
      'basics': {
        'type': 'object',
        'properties': {
          'name': {'type': 'string'},
          'email': {'type': 'string'},
          'phone': {'type': 'string'},
          'location': {'type': 'string'},
          'city': {'type': 'string'},
          'country': {'type': 'string'},
          'years_of_experience': {'type': 'integer'},
          'current_role': {'type': 'string'},
          'current_company': {'type': 'string'},
        },
        'required': ['name']
      },
      'summary': {'type': 'string'},
      'highlights': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Top 5-10 most impressive achievements'
      },
      'gaps': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Missing or weak areas in the profile'
      },
      'skills': {
        'type': 'array',
        'items': {
          'type': 'object',
          'properties': {
            'name': {'type': 'string'},
            'level': {'type': 'string', 'enum': ['beginner', 'intermediate', 'advanced', 'expert']},
            'years': {'type': 'number'},
            'category': {'type': 'string'},
          },
          'required': ['name', 'level']
        }
      },
      'work_experience': {
        'type': 'array',
        'items': {
          'type': 'object',
          'properties': {
            'company': {'type': 'string'},
            'title': {'type': 'string'},
            'start_date': {'type': 'string'},
            'end_date': {'type': 'string'},
            'description': {'type': 'string'},
            'highlights': {'type': 'array', 'items': {'type': 'string'}},
            'tech_stack': {'type': 'array', 'items': {'type': 'string'}},
            'role': {'type': 'string'},
          },
          'required': ['company', 'title']
        }
      },
      'education': {
        'type': 'array',
        'items': {
          'type': 'object',
          'properties': {
            'school': {'type': 'string'},
            'degree': {'type': 'string'},
            'field': {'type': 'string'},
            'graduation': {'type': 'string'},
            'gpa': {'type': 'string'},
            'honors': {'type': 'array', 'items': {'type': 'string'}},
          }
        }
      },
      'projects': {
        'type': 'array',
        'items': {
          'type': 'object',
          'properties': {
            'name': {'type': 'string'},
            'description': {'type': 'string'},
            'url': {'type': 'string'},
            'highlights': {'type': 'array', 'items': {'type': 'string'}},
            'role': {'type': 'string'},
            'tech_stack': {'type': 'array', 'items': {'type': 'string'}},
            'duration': {'type': 'string'},
          }
        }
      },
      'languages': {
        'type': 'array',
        'items': {
          'type': 'object',
          'properties': {
            'name': {'type': 'string'},
            'proficiency': {'type': 'string'},
          }
        }
      },
      'certifications': {
        'type': 'array',
        'items': {'type': 'string'}
      },
      'validation_warnings': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Issues found by the 5 self-validation checks'
      },
      'target_roles': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Inferred target roles based on experience'
      },
    },
    'required': ['basics', 'summary', 'skills', 'work_experience']
  }
}
