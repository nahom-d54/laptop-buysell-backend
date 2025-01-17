# Laptop Buy/Sell Backend

Welcome to the Laptop Buy/Sell Backend project! This repository contains the backend code for a platform where users can buy and sell laptops. The backend is built using Django, and it connects to a PostgreSQL database. Additionally, it uses Pyrogram to scrape laptops from various Telegram groups and channels, and Cloudflare S3 to store images.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Installation

To get started with the project, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/nahom-d54/laptop-buysell-backend.git
   cd laptop-buysell-backend
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add the following variables:

   ```env
   SECRET_KEY=your_secret_key
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=your_database_url
   TELEGRAM_API_ID=your_telegram_api_id
   TELEGRAM_API_HASH=your_telegram_api_hash
   TELEGRAM_SESSIONS=your_telegram_session
   S3_TOKEN_VALUE='tokenvalue'
   S3_ACCESS_KEY_ID='yourkeyid'
   S3_SECRET_ACCESS_KEY='youracesskey'
   S3_ENDPOINT_URL='https://<hash>.r2.cloudflarestorage.com'
   S3_BUCKET_NAME='assets'
   S3_CUSTOM_DOMAIN='<subdomain>.<yourdomain>.<com>'
   SCHEDULE_INTERVAL='30'
   TELEGRAM_CHANNELS='-1001305166794,-1001371878805,-1001412045489,-1001209915715,-1001454837810,-1002078207169,-1001291136913,-1001716754483,-1002099805276,-1001493631129,-1001929624541,-1002207576225,-1001257945444,-1001590914141,-1001418172821,-1001378978267,-1001966011461,-1001195361398,-1001632860452, -1001346810747,-1001121667766'
   ENV='production'
   ```

5. **Apply migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Start the server:**
   ```bash
   python manage.py runserver
   ```

## Usage

Once the server is running, you can access the API at `http://localhost:8000`. Use tools like Postman or cURL to interact with the endpoints.

## API Endpoints

Here are some of the main API endpoints:

- **User Registration:**

  - `POST /api/users/register/`
  - Request body: `{ "username": "example", "password": "password123" }`

- **User Login:**

  - `POST /api/users/login/`
  - Request body: `{ "username": "example", "password": "password123" }`

- **List Laptops for Sale:**

  - `GET /api/laptops/`

- **Add a Laptop for Sale:**

  - `POST /api/laptops/`
  - Request body: `{ "brand": "Dell", "model": "XPS 13", "price": 1000 }`

- **Delete a Laptop:**
  - `DELETE /api/laptops/:id/`

## Contributing

We welcome contributions from the community! To contribute, follow these steps:

1. **Fork the repository** 🍴
2. **Clone your fork** 🛠️

   ```bash
   git clone https://github.com/nahom-d54/laptop-buysell-backend.git
   cd laptop-buysell-backend
   ```

3. **Create a new branch** 🌿

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes** ✨

5. **Commit your changes** 💾

   ```bash
   git commit -m "Add your commit message"
   ```

6. **Push to your branch** 🚀

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** 🔄

Please ensure your code follows our coding standards and includes tests where applicable.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

Happy coding! 🎉

## Additional Resources

For more information on Django, PostgreSQL, Pyrogram, Cloudflare S3, and other technologies used in this project, check out the following resources:

- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pyrogram Documentation](https://docs.pyrogram.org/)
- [Cloudflare S3 Documentation](https://developers.cloudflare.com/r2/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

If you encounter any issues or have questions, feel free to open an issue or reach out to the community for help. We appreciate your feedback and contributions to make this project better!

## Contact

For any inquiries or support, you can reach me at nahom@nahom.eu.org.

Thank you for your interest in the Laptop Buy/Sell Backend project. We hope you find it useful and look forward to your contributions!

Happy coding! 🎉
