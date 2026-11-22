plugins {
    id("com.android.application")
}

android {
    namespace = "app.czds.xash3d.launcher"
    compileSdk = 34

    defaultConfig {
        applicationId = "app.czds.xash3d.launcher"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "0.1-experimental"

        ndk {
            abiFilters.addAll(listOf("arm64-v8a", "armeabi-v7a"))
        }
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
        }
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    packaging {
        jniLibs {
            useLegacyPackaging = true
        }
    }

    lint {
        abortOnError = false
    }
}
