# Yonoma Email Marketing Python SDK

The official **Python** client library for the **Yonoma Email Marketing API**.

---

## Installation**

### Install via **pip**:
```sh
pip install yonoma
```

or manually install from GitHub:
```sh
pip install git+https://github.com/YonomaHQ/yonoma-python
```

---

## **Quick Start**

### **Note:** This SDK requires **Python 3.7 or above**.

```python
from yonoma import Yonoma

# Initialize the client
yonoma = Yonoma(api_key="YOUR-API-KEY")
```

### **Send your email**
```python
response = yonoma.email.send({
    'from_email': 'updates@yonoma.io',
     'to_email': 'email@yourdomain.com',
     'subject':"Welcome to Yonoma - You're In!",
     'mail_template': "We're excited to welcome you to Yonoma! Your successful signup marks the beginning of what we hope will be an exceptional journey."
    })
print(response)
```

---

# **Features**

## **Lists**

### **Create a new list**
```python
response = yonoma.lists.create('list_name':'New group')
print(response)
```

### **Get a list of Lists**
```python
response = yonoma.lists.list()
print(response)
```

### **Retrieve a specific list**
```python
response = yonoma.lists.retrieve("list_id")
print(response)
```

### **Update a list**
```python
response = yonoma.lists.update('list_id', {'list_name': 'Upadated list name'})
print(response)
```

### **Delete a list**
```python
response = yonoma.lists.delete('list_id')
print(response)
```

---

## **Tags**

### **Create a new tag**
```python
response = yonoma.tags.create({'tag_name': 'New tag'})
print(response)
```

### **Get a list of tags**
```python
response = yonoma.tags.list()
print(response)
```

### **Retrieve a specific tag**
```python
response = yonoma.tags.retrieve('tag_id')
print(response)
```

### **Update a tag**
```python
response = yonoma.tags.update('tag_id', {'tag_name': 'Updated Tag Name'})
print(response)
```

### **Delete a tag**
```python
response = Tags.delete('tag_id')
print(response)
```

---

## **Contacts**

### **Create a new contact**
```python
response = yonoma.contacts.create("list_id",
    {
        email: "email@example.com",
        status: "Subscribed" | "Unsubscribed",
        data: {
            firstName: string,
            lastName: string,
            phone: string,
            gender: string,
            address: string,
            city: string,
            state: string,
            country: string,
            zipcode: string,
        }
    }
)
print(response)
```

### **Update a contact**
```python
response = yonoma.contacts.update('list_id','contact_id',{
    'status': "Subscribed" | "Unsubscribed" 
}
)
print(response)
```

### **Add a tag to a contact**
```python
response = yonoma.contacts.addtag('contact_id', {
    'tag_id': 'Tag id'
})
print(response)
```

### **Remove a tag from a contact**
```python
response = yonoma.contacts.removetag('contact_id', {
    'tag_id': 'Tag id'
})
print(response)
```

---

## **Useful Links**

- **PyPI Package**: [Yonoma on PyPI](https://pypi.org/project/yonoma/)
- **GitHub Repository**: [Yonoma GitHub](https://github.com/YonomaHQ/yonoma-python)
- **Yonoma API Docs**: [Yonoma API Documentation](https://yonoma.io/api-reference/introduction)

---

## **License**
This package is licensed under the **MIT License**.

---

This is the **official Python SDK** for **Yonoma Email Marketing**, providing seamless API integrations.

