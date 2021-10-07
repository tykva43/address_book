from yoyo import step

steps = [
    step("CREATE TYPE gender_type AS ENUM ('male', 'female')"),
    # Create users table
    step(
        # Apply step
        "CREATE TABLE users (id BIGSERIAL PRIMARY KEY NOT NULL, "
        "name VARCHAR(70) NOT NULL, "
        "photo_path VARCHAR(250) NOT NULL, "
        "gender gender_type NOT NULL, "
        "born_at DATE NOT NULL, "
        "address VARCHAR(150) NOT NULL);",
        # Rollback step
        "DROP TABLE users"
    ),
    step("CREATE TYPE phone_type AS ENUM ('mobile', 'city')"),
    # Create phones table
    step(
        # Apply step
        "CREATE TABLE phones (id BIGSERIAL PRIMARY KEY NOT NULL, "
        "user_id BIGINT NOT NULL, "
        "type phone_type NOT NULL, "
        "number VARCHAR(20) NOT NULL, "
        "FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE);",
        # Rollback step
        "DROP TABLE phones"
    ),
    step("CREATE TYPE email_type AS ENUM ('personal', 'work')"),
    # Create emails table
    step(
        # Apply step
        "CREATE TABLE emails (id BIGSERIAL PRIMARY KEY NOT NULL, "
        "user_id BIGINT NOT NULL, "
        "type email_type NOT NULL, "
        "email VARCHAR(255), "
        "FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE);",
        # Rollback step
        "DROP TABLE emails"
    )
]
