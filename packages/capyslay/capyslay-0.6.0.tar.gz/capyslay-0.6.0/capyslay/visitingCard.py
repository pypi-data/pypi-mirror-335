def visitingCard():
    return [
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
            xmlns:app="http://schemas.android.com/apk/res-auto"
            xmlns:tools="http://schemas.android.com/tools"
            android:id="@+id/main"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical"
            tools:context=".MainActivity">

            <RelativeLayout
                android:layout_width="match_parent"
                android:layout_height="125dp">
                
                <TextView
                    android:id="@+id/textView"
                    android:layout_width="match_parent"
                    android:layout_height="match_parent"
                    android:layout_centerInParent="true"
                    android:text="COMPANY NAME"
                    android:textAllCaps="true"
                    android:textAlignment="center"
                    android:textColorLink="#FF5722"
                    android:textSize="24sp" />
                
                <ImageView
                    android:id="@+id/imageView"
                    android:layout_width="120dp"
                    android:layout_height="103dp"
                    android:layout_alignParentEnd="true"
                    android:layout_marginEnd="16dp"
                    app:srcCompat="@drawable/rvr" />
            </RelativeLayout>

            <View
                android:id="@+id/view"
                android:layout_width="match_parent"
                android:layout_height="2dp"
                android:background="@color/black" />

            <TextView
                android:id="@+id/textView2"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Name"
                android:textAlignment="center"
                android:textColor="#3F51B5"
                android:textSize="24sp"
                android:textStyle="italic" />
                
            <TextView
                android:id="@+id/textView3"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Job Title"
                android:textAlignment="center"
                android:textSize="20sp"
                android:textStyle="italic" />

            <TextView
                android:id="@+id/textView4"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Phone Number"
                android:textAlignment="center"
                android:textSize="20sp"
                android:textStyle="italic" />

            <TextView
                android:id="@+id/textView5"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Address"
                android:textAlignment="center"
                android:textSize="20sp"
                android:textStyle="italic" />

            <TextView
                android:id="@+id/textView6"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Email"
                android:textAlignment="center"
                android:textSize="20sp"
                android:textStyle="italic" />
        </LinearLayout>
        """,
        """
        package com.example.program1viscard;

        import android.os.Bundle;

        import androidx.activity.EdgeToEdge;
        import androidx.appcompat.app.AppCompatActivity;
        import androidx.core.graphics.Insets;
        import androidx.core.view.ViewCompat;
        import androidx.core.view.WindowInsetsCompat;

        public class MainActivity extends AppCompatActivity {

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                EdgeToEdge.enable(this);
                setContentView(R.layout.activity_main);
                ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
                    Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
                    v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
                    return insets;
                });
            }
        }
        """
    ]