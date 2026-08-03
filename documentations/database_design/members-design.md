## Entities
```text
1. GeneralBenefits
2. Benefits
3. Category
4. AssociatedHungarianCompany
5. MembershipRequiredDocument
6. GeneralApplication
7. MembershipApplication
8. IndividualApplication
9. CorporateApplication
10. Profile
11. Member
12. MemberRepresentative
13. MembershipApplicationDocument
```
## Profile
- Stores the personal/bio data of a member or member representative.
- Includes title, nationality, first name, last name, email, and phone number.

## Category
- Defines a membership category or application type.
- Examples: Individual and Corporate.
- Stores category information such as description, annual fee, and active status.

## Membership Application
- The main application record.
- Stores the application type/category, application number, proposer,
  associated Hungarian company, application status, review information,
  and date joined.
- Acts as the central record connecting the application to its
  related information.

## General Application
- Stores information shared by both Individual and Corporate applications.
- Includes proposer information, business interests, interest in Hungary,
  challenges, areas where the chamber can assist, and declaration details.

## Individual Application
- Stores information specific to an Individual membership application.
- Includes registered business name, office telephone, and type of business.
- Belongs to one Membership Application.

## Corporate Application
- Stores information specific to a Corporate membership application.
- Includes company information, business information, registration details,
  employee count, year established, and website.
- Belongs to one Membership Application.

## Member
- Represents an approved or registered member.
- Connects a Profile to a Membership Application.

## Member Representative
- Represents a corporate member's representative.
- Connects a Profile to a Membership Application.
- Stores representative type and position.
- Examples: Primary Representative and Alternative Representative.

## Associated Hungarian Company
- Stores the basic information of a Hungarian company associated with
  a Membership Application.

## Membership Required Document
- Defines the documents required for a particular membership category.
- Stores document title, description, requirement status, and display order.

## Membership Application Document
- Stores documents uploaded for a Membership Application.
- Connects an uploaded file to its required document type.
- Stores document verification information.

## General Benefits
- Stores benefits that apply to all membership categories.

## Specific Benefits
- Stores benefits assigned to a particular membership category.

## Individual Benefits
- Represents the complete benefits available to the Individual category,
  including general benefits and benefits specific to the Individual category.

## Corporate Benefits
- Represents the complete benefits available to the Corporate category,
  including general benefits and benefits specific to the Corporate category.

## Diagram
```text
                              Category
                                 │
                                 │
                     MembershipApplication
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          │                      │                      │
 GeneralApplication     AssociatedHungarianCompany    Documents
          │
          │
          ├──────────────────────┐
          │                      │
          │                      │
IndividualApplication   CorporateApplication
          │                      │
          └──────────────┬───────┘
                         │
             Application-specific details


                     MembershipApplication
                         │
          ┌──────────────┴──────────────┐
          │                             │
        Member              MemberRepresentative
          │                             │
       Profile                         Profile


GeneralBenefits
       │
       ├── Individual Category Benefits
       │
       └── Corporate Category Benefits


SpecificBenefits
       │
       ├── Individual-specific benefits
       │
       └── Corporate-specific benefits
```


Membership Dashboard
│
├── Dashboard Overview
│   ├── Total members
│   ├── Individual members
│   ├── Corporate members
│   ├── Pending applications
│   ├── Application status summary
│   ├── Membership type summary
│   ├── Director proposal statistics
│   └── Recent applications
│
├── Membership Applications
│   ├── View all applications
│   ├── Individual applications
│   ├── Corporate applications
│   ├── Search applications
│   ├── View application details
│   ├── Review application
│   ├── Approve application
│   ├── Reject application
│   ├── Suspend application
│   └── View uploaded documents
│
├── Members
│   ├── All members
│   ├── Individual members
│   ├── Corporate members
│   ├── Search by first name
│   ├── Search by last name
│   ├── Search by full name
│   ├── Search by email
│   ├── Filter by date joined
│   ├── View member profile
│   ├── View membership details
│   └── View representatives
│
├── Benefits
│   ├── General benefits
│   │   ├── Add
│   │   ├── View
│   │   ├── Edit
│   │   ├── Delete
│   │   ├── Activate
│   │   └── Deactivate
│   │
│   └── Category-specific benefits
│       ├── Individual benefits
│       ├── Corporate benefits
│       ├── Add
│       ├── View
│       ├── Edit
│       ├── Delete
│       ├── Activate
│       └── Deactivate
│
├── Required Documents
│   ├── Individual requirements
│   │   ├── Passport
│   │   └── Business registration document
│   │
│   ├── Corporate requirements
│   │   ├── Passport
│   │   └── CAC document
│   │
│   ├── Add document requirement
│   ├── Edit document requirement
│   ├── Delete document requirement
│   ├── Set required or optional
│   ├── Activate or deactivate
│   └── Set display order
│
└── Associated Hungarian Companies
    ├── View all companies
    ├── Search companies
    ├── Add company
    ├── View company
    ├── Edit company
    ├── Delete company
    └── View applications linked to company