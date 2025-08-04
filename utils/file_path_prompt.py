file_path_prompt = """Analyze the provided code block and its programming language. Based on the code's functionality and common project conventions for that language, suggest a single, plausible file path:
<file_path>
parent_folders/file_path.extension
</file_path>

<example>
<language>
rust
</language>
<code>
use std::fs;
use std::io;
use std::path::Path;

/// Reads the entire content of a file into a string.
pub fn read_file_to_string<P: AsRef<Path>>(path: P) -> io::Result<String> {
    fs::read_to_string(path)
}
</code>
<file_path>
data_processor/src/utils/io.rs
</file_path>
</example>

<example>
<language>
javascript
</language>
<code>
import React from 'react';

const UserProfileCard = ({ user }) => {
    if (!user) {
        return <div>Loading...</div>;
        }

    return (
        <div className="profile-card">
        <img src={user.avatarUrl} alt={${user.name}'s avatar} />
        <h2>{user.name}</h2>
        <p>@{user.username}</p>
        </div>
    );
};

export default UserProfileCard;
</code>
<file_path>
my-webapp/src/components/UserProfileCard.jsx
</file_path>
</example>

<example>
<language>
python
</language>
<code>
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
</code>
<file_path>
data_pipeline/core/db/database_setup.py
</file_path>
</example>

example>
<language>
java
</language>
<code>
package com.ecommerce.app.models;

import javax.persistence.Entity;
import javax.persistence.Id;
import java.math.BigDecimal;

@Entity
public class Product {

    @Id
    private Long id;
    private String name;
    private String description;
    private BigDecimal price;

    // Constructors, getters, and setters omitted for brevity
}
</code>
<file_path>
online-store-api/src/main/java/com/ecommerce/app/models/Product.java
</file_path>
</example>

<example>
<language>
cpp
</language>
<code>
#pragma once

#include <vector>
#include <stdexcept>

namespace Engine {
    class AudioBuffer {
        public:
            AudioBuffer(size_t size);
            void write(const std::vector<float>& data);
            float read_sample(size_t index) const;
            size_t get_size() const;

        private:
            std::vector<float> buffer_;
    };
}
</code>
<file_path>
game_engine/include/audio/AudioBuffer.hpp
</file_path>
</example>
"""
